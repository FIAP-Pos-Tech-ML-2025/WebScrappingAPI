import httpx
from bs4 import BeautifulSoup, Tag
from typing import List, Dict, Optional, Tuple, Any
import re
from asyncio import gather

from ..config import settings

OPCAO_MAP = {
    "producao": "opt_02",
    "processamento": "opt_03",
    "comercializacao": "opt_04",
    "importacao": "opt_05",
    "exportacao": "opt_06",
}

async def _make_request(url: str, params: Optional[Dict[str, Any]] = None) -> BeautifulSoup:
    """Helper function to make HTTP GET request and return BeautifulSoup soup."""
    base_url_to_use = settings.TARGET_BASE_URL
    if not base_url_to_use.endswith('/'):
        base_url_to_use += '/'
    
    full_url = f"{base_url_to_use}{url.lstrip('/')}"

    async with httpx.AsyncClient(
        headers={"User-Agent": settings.USER_AGENT or "Mozilla/5.0"},
        timeout=settings.TIMEOUT,
        follow_redirects=True
    ) as client:
        try:
            print(f"Requesting URL: {full_url} with params: {params}")
            response = await client.get(full_url, params=params)
            response.raise_for_status()
            print(f"Response status: {response.status_code} for {response.url}")
            return BeautifulSoup(response.text, "html.parser")
        except httpx.HTTPStatusError as exc:
            error_message = f"HTTP error {exc.response.status_code} while fetching {exc.request.url}"
            try:
                error_message += f": {exc.response.text[:500]}"
            except Exception:
                pass
            raise Exception(error_message) from exc
        except httpx.RequestError as exc:
            raise Exception(f"Request error while fetching {exc.request.url}: {exc}") from exc

async def get_available_suboptions(section_opcao: str) -> List[Dict[str, str]]:
    if section_opcao not in [OPCAO_MAP["processamento"], OPCAO_MAP["importacao"], OPCAO_MAP["exportacao"]]:
        return []
    
    soup = await _make_request("index.php", params={"opcao": section_opcao})
    suboptions: List[Dict[str, str]] = []
    
    buttons = soup.find_all("button", attrs={"name": "subopcao"})

    for button in buttons:
        value = button.get("value")
        name = ' '.join(button.get_text(strip=True).split())
        if value and name and ("btn_sopt" in button.get("class", []) or value.startswith("subopt_")):
            suboptions.append({"name": name, "value": value})
            
    if not suboptions:
        print(f"Warning: Could not find suboption buttons for {section_opcao} using main selectors.")
    return suboptions

async def get_year_range(section_opcao: str, subopcao_value: Optional[str] = None) -> Tuple[Optional[int], Optional[int]]:
    url_params = {"opcao": section_opcao}
    if subopcao_value:
        url_params["subopcao"] = subopcao_value
    
    soup = await _make_request("index.php", params=url_params)
    year_range_text_element = None
    
    label_element = soup.find("label", class_="lbl_pesq", string=re.compile(r"Ano:\s*\[\d{4}-\d{4}\]"))
    if label_element:
        year_range_text_element = label_element.get_text(strip=True)
    
    if not year_range_text_element: # Fallback if specific label not found
        text_nodes = soup.find_all(string=re.compile(r"Ano:\s*\[\d{4}-\d{4}\]"))
        if text_nodes:
            year_range_text_element = str(text_nodes[0]) # Take the first match

    if not year_range_text_element:
        print(f"Warning: Could not find year range text for {section_opcao} (suboption: {subopcao_value}).")
        return None, None

    match = re.search(r"\[(\d{4})-(\d{4})\]", year_range_text_element)
    if match:
        min_year = int(match.group(1))
        max_year = int(match.group(2))
        return min_year, max_year
    
    print(f"Warning: Could not parse year range from '{year_range_text_element}' for {section_opcao} (suboption: {subopcao_value}).")
    return None, None

def _parse_single_year_summary_table(soup: BeautifulSoup, year_fetched: int, 
                                     suboption_name: Optional[str] = None,
                                     section_opcao_for_debug: str = "") -> List[Dict[str, Any]]:
    """
    Parses tables that generally show an 'item' column and one or more 'value' columns for a single year.
    Adaptable for Produção, Comercialização, Processamento, Importação, Exportação based on their HTML.
    """
    data_table: Optional[Tag] = None
    data_table = soup.find("table", class_="tb_dados") 
    if not data_table:
        data_table = soup.find("table", class_="tb_base")
        if data_table and not data_table.find("table", class_="tb_dados"):
            pass
        elif data_table:
            data_table = data_table.find("table", class_="tb_dados")

    if not data_table:
        all_tables = soup.find_all("table")
        for t in all_tables:
            if t.find("td", class_=["tb_item", "tb_subitem"]): # Check for known item classes
                data_table = t
                break
        if not data_table and all_tables:
             data_table = max(all_tables, key=lambda t_item: len(t_item.find_all("tr", recursive=False)), default=None)


    if not data_table:
        print(f"Warning: Could not find a suitable data table for {section_opcao_for_debug} (suboption: {suboption_name}, year: {year_fetched}). Soup head: {str(soup)[:500]}")
        return []

    extracted_data: List[Dict[str, Any]] = []
    header_row = data_table.find("thead") # Headers are usually in <thead>
    if header_row:
        header_row = header_row.find("tr")
    
    if not header_row: # Fallback if no <thead> or <tr> in <thead>
        header_row = data_table.find("tr") # Assume first <tr> has headers
        
    if not header_row:
        print(f"Warning: No header row found in table for {section_opcao_for_debug}.")
        return []

    headers = [ ' '.join(h.get_text(strip=True).split()) for h in header_row.find_all(["th", "td"])]
    if not headers:
        print(f"Warning: No headers extracted from header row for {section_opcao_for_debug}.")
        return []

    item_col_idx = 0 
    item_col_name = headers[0] if headers else "Item"

    value_col_indices = list(range(1, len(headers)))
    value_col_names = headers[1:] if len(headers) > 1 else ["Valor"]


    current_main_category = None
    body = data_table.find("tbody")
    if not body:
        print(f"Warning: No tbody found in table for {section_opcao_for_debug}. Will try to parse all <tr> after header.")
        rows_to_parse = data_table.find_all("tr")[1:]
    else:
        rows_to_parse = body.find_all("tr")

    for row in rows_to_parse:
        cells = row.find_all(["td", "th"])

        if len(cells) == 1 and cells[0].get("colspan"):
            category_text = ' '.join(cells[0].get_text(strip=True).split())
            if category_text.lower() != "total":
                current_main_category = category_text
            continue
        
        if cells and ("tb_item" in cells[0].get("class", []) and len(cells) == len(headers) and not cells[0].get("colspan")):
             current_main_category = ' '.join(cells[0].get_text(strip=True).split())
        
        if not cells or len(cells) != len(headers):
            # print(f"Skipping row due to cell count mismatch: {len(cells)} cells, {len(headers)} headers. Row: {row.get_text(strip=True)[:100]}")
            continue
        
        item_name = ' '.join(cells[item_col_idx].get_text(strip=True).split())
        if not item_name or item_name.lower() == "total":
            continue

        data_item: Dict[str, Any] = {item_col_name: item_name}
        data_item["Ano"] = year_fetched
        if suboption_name:
            data_item["Subopcao_Selecionada"] = suboption_name
        if current_main_category and item_name != current_main_category and "tb_subitem" in cells[item_col_idx].get("class", []):
            data_item["Categoria_Principal"] = current_main_category
        
        has_values = False
        for i, col_idx in enumerate(value_col_indices):
            value_str = ' '.join(cells[col_idx].get_text(strip=True).split())
            data_item[value_col_names[i]] = value_str if value_str and value_str != "-" else "0"
            if value_str and value_str != "-":
                has_values = True
        
        if has_values or len(headers) == 1:
            extracted_data.append(data_item)
            
    return extracted_data

async def fetch_embrapa_data(section_opcao: str,
                             year_to_fetch: Optional[int] = None,
                             all_years: bool = False,
                             subopcao_value: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
    """ Main data fetching and parsing orchestrator. """
    
    suboption_name_for_data = None
    if subopcao_value and section_opcao in [OPCAO_MAP["processamento"], OPCAO_MAP["importacao"], OPCAO_MAP["exportacao"]]:
        available_subs = await get_available_suboptions(section_opcao)
        for sub in available_subs:
            if sub['value'] == subopcao_value:
                suboption_name_for_data = sub['name']
                break
    
    if all_years:
        min_year, max_year = await get_year_range(section_opcao, subopcao_value)
        if min_year is None or max_year is None:
            raise ValueError(f"Could not determine year range for {section_opcao}/{subopcao_value} to fetch all years.")
        
        aggregated_data: List[Dict[str, Any]] = []
        tasks = []
        year_list_for_tasks = list(range(min_year, max_year + 1))

        for year in year_list_for_tasks:
            params = {"opcao": section_opcao, "ano": year}
            if subopcao_value:
                params["subopcao"] = subopcao_value
            
            tasks.append(_make_request("index.php", params=params))
        
        page_soups = await gather(*tasks, return_exceptions=True)
        
        for i, soup_or_exc in enumerate(page_soups):
            year = year_list_for_tasks[i]
            if isinstance(soup_or_exc, Exception):
                print(f"Failed to fetch page for {section_opcao}/{subopcao_value} year {year}: {soup_or_exc}")
                continue
            try:
                year_data = _parse_single_year_summary_table(soup_or_exc, year, suboption_name_for_data, section_opcao_for_debug=section_opcao)
                aggregated_data.extend(year_data)
            except Exception as e:
                print(f"Failed to parse data for {section_opcao}/{subopcao_value} year {year}: {e}")
        return {"data": aggregated_data}
        
    elif year_to_fetch:
        params = {"opcao": section_opcao, "ano": year_to_fetch}
        if subopcao_value:
            params["subopcao"] = subopcao_value
        
        soup = await _make_request("index.php", params=params)
        parsed_data = _parse_single_year_summary_table(soup, year_to_fetch, suboption_name_for_data, section_opcao_for_debug=section_opcao)
        return {"data": parsed_data}
    else:
        raise ValueError("Year must be specified or all_years=True.")