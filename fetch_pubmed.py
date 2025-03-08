import requests
import xmltodict
import pandas as pd
import argparse

BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
COMPANY_KEYWORDS = [
    "Pharmaceutical", "Biotech", "Biotechnology", "Therapeutics", "Pharma",
    "BioPharma", "Life Sciences", "Biosciences", "Drug Development",
    "Medicines", "Inc.", "Ltd.", "Corp.", "GmbH", "S.A.", "S.p.A.", "LLC"
]

def search_pubmed(query, max_results=100, debug=False):
    """Search PubMed for papers only and return PMIDs."""
    params = {
        "db": "pubmed",
        "term": f"{query}",  # Removed the filter to get more results
        "retmax": max_results,
        "retmode": "json",
        "sort": "date"  # Sort by date to get recent results
    }
    
    if debug:
        print(f"[DEBUG] Sending request to PubMed with params: {params}")
    
    response = requests.get(BASE_URL + "esearch.fcgi", params=params)
    
    if debug:
        print(f"[DEBUG] PubMed Search URL: {response.url}")

    if response.status_code == 200:
        result = response.json()
        id_list = result.get("esearchresult", {}).get("idlist", [])
        if debug:
            print(f"[DEBUG] Found {len(id_list)} PMIDs")
        return id_list
    
    print(f"Error fetching PubMed search results: {response.status_code}")
    return []

def fetch_paper_details(pmids, debug=False):
    """Fetches paper details from PubMed."""
    if not pmids:
        return None
        
    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml"
    }
    
    if debug:
        print(f"[DEBUG] Fetching details for {len(pmids)} PMIDs")
    
    response = requests.get(BASE_URL + "efetch.fcgi", params=params)
    
    if debug:
        print(f"[DEBUG] PubMed Fetch URL: {response.url}")
        print(f"[DEBUG] Response status: {response.status_code}")

    if response.status_code == 200:
        return response.text
    
    print(f"Error fetching paper details: {response.status_code}")
    return None

def extract_paper_data(xml_data, debug=False):
    """Parses XML data and extracts relevant details."""
    if debug:
        print("[DEBUG] Starting XML parsing...")
    
    data_dict = xmltodict.parse(xml_data)
    papers = []
    
    # Handle single article case by converting to list
    articles = data_dict.get("PubmedArticleSet", {}).get("PubmedArticle", [])
    if not isinstance(articles, list):
        articles = [articles]

    if debug:
        print(f"[DEBUG] Found {len(articles)} articles to process")

    for article in articles:
        try:
            pmid = article["MedlineCitation"]["PMID"]["#text"]
            article_info = article["MedlineCitation"]["Article"]
            title = article_info.get("ArticleTitle", "No Title")
            
            # Handle different date formats
            pub_date_info = article_info.get("Journal", {}).get("JournalIssue", {}).get("PubDate", {})
            if "Year" in pub_date_info:
                pub_date = pub_date_info["Year"]
            elif "MedlineDate" in pub_date_info:
                pub_date = pub_date_info["MedlineDate"].split()[0]
            else:
                pub_date = "Unknown Date"

            # Handle author list
            author_list = article_info.get("AuthorList", {})
            if author_list:
                authors = author_list.get("Author", [])
                if not isinstance(authors, list):
                    authors = [authors]
            else:
                authors = []

            non_academic_authors = []
            
            for author in authors:
                if "AffiliationInfo" in author:
                    affiliations = author["AffiliationInfo"]
                    if not isinstance(affiliations, list):
                        affiliations = [affiliations]
                    
                    author_name = f"{author.get('ForeName', '')} {author.get('LastName', '')}".strip()
                    
                    for affiliation_info in affiliations:
                        affiliation = affiliation_info.get("Affiliation", "")
                        if any(keyword.lower() in affiliation.lower() for keyword in COMPANY_KEYWORDS):
                            non_academic_authors.append(f"{author_name} ({affiliation})")
                            break

            # Add paper if it has non-academic authors
            if non_academic_authors:
                papers.append({
                    "PMID": pmid,
                    "Title": title,
                    "Publication Date": pub_date,
                    "Non-Academic Authors": "; ".join(non_academic_authors),
                    "Corresponding Author Email": "Not Available"
                })
                
                if debug:
                    print(f"[DEBUG] Added paper {pmid} with {len(non_academic_authors)} non-academic authors")

        except Exception as e:
            if debug:
                print(f"[DEBUG] Error processing article: {str(e)}")
            continue

    if debug:
        print(f"[DEBUG] Total papers with non-academic authors: {len(papers)}")

    return papers

def save_to_csv(papers, filename):
    """Saves extracted papers data to a CSV file."""
    df = pd.DataFrame(papers)
    df.to_csv(filename, index=False)
    print(f"\nResults saved to {filename}")

def main():
    parser = argparse.ArgumentParser(description="Fetch PubMed papers related to a topic and extract pharmaceutical/biotech affiliations.")
    parser.add_argument("query", type=str, help="Search term for PubMed (e.g., 'mRNA vaccine')")
    parser.add_argument("-m", "--max", type=int, default=100, help="Maximum number of results to fetch (default: 100)")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode to print extra execution details")
    parser.add_argument("-f", "--file", type=str, help="Output file name (CSV). If not provided, prints to console.")

    args = parser.parse_args()

    if args.debug:
        print("[DEBUG] Arguments:", args)

    print("\nSearching PubMed for:", args.query)
    pmids = search_pubmed(args.query, max_results=args.max, debug=args.debug)

    if not pmids:
        print("No articles found.")
        return
    
    print("\nFetching article details...")
    xml_data = fetch_paper_details(pmids, debug=args.debug)

    if not xml_data:
        print("No data retrieved.")
        return

    print("\nExtracting required details...")
    papers = extract_paper_data(xml_data, debug=args.debug)

    if papers:
        if args.file:
            save_to_csv(papers, args.file)
            print(f"\nSaved {len(papers)} papers with non-academic authors to {args.file}")
        else:
            print("\nExtracted Papers:")
            for paper in papers:
                print(f"PMID: {paper['PMID']}, Title: {paper['Title']}, Date: {paper['Publication Date']}")
                print(f"Non-Academic Authors: {paper['Non-Academic Authors']}")
                print(f"Corresponding Email: {paper['Corresponding Author Email']}\n")
    else:
        print("No papers found with non-academic authors.")

if __name__ == "__main__":
    main()
