from typing import List, Dict, Any, Optional
from serpapi import GoogleSearch
import logging

logger = logging.getLogger(__name__)


class SerpAPIService:
    """
    Service for fetching Google Ads data using SerpAPI.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key

    def search_ads(
        self,
        keyword: str,
        location: Optional[str] = None,
        device: str = "desktop",
        gl: str = "us",  # Country code
    ) -> List[Dict[str, Any]]:
        """
        Search for Google Ads using SerpAPI.

        Args:
            keyword: Search keyword
            location: Geographic location
            device: desktop, mobile, or tablet
            gl: Country code (us, uk, ca, etc.)

        Returns:
            List of parsed ad data
        """
        try:
            # Build search params
            params = {
                "q": keyword,
                "api_key": self.api_key,
                "engine": "google",
                "gl": gl,
                "device": device,
            }

            if location:
                params["location"] = location

            # Execute search
            search = GoogleSearch(params)
            results = search.get_dict()

            # Parse ads from results
            ads = self._parse_ads(results, keyword, location, device)

            logger.info(f"Found {len(ads)} ads for keyword: {keyword}")

            return ads

        except Exception as e:
            logger.error(f"Error fetching ads from SerpAPI: {str(e)}")
            raise

    def _parse_ads(
        self,
        results: Dict[str, Any],
        keyword: str,
        location: Optional[str],
        device: str,
    ) -> List[Dict[str, Any]]:
        """
        Parse SerpAPI results into our ad data format.
        """
        ads = []

        # Top ads (appear above organic results)
        if "ads" in results:
            for idx, ad in enumerate(results["ads"]):
                parsed_ad = self._parse_single_ad(
                    ad, keyword, location, device, idx + 1, is_top=True
                )
                if parsed_ad:
                    ads.append(parsed_ad)

        # Bottom ads (appear below organic results)
        if "ads_bottom" in results:
            for idx, ad in enumerate(results["ads_bottom"]):
                parsed_ad = self._parse_single_ad(
                    ad, keyword, location, device, idx + 1, is_top=False
                )
                if parsed_ad:
                    ads.append(parsed_ad)

        # Shopping ads
        if "shopping_results" in results:
            for idx, ad in enumerate(results["shopping_results"]):
                parsed_ad = self._parse_shopping_ad(
                    ad, keyword, location, device, idx + 1
                )
                if parsed_ad:
                    ads.append(parsed_ad)

        return ads

    def _parse_single_ad(
        self,
        ad: Dict[str, Any],
        keyword: str,
        location: Optional[str],
        device: str,
        position: int,
        is_top: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """
        Parse a single text ad from SerpAPI.
        """
        try:
            # Extract domain from link or displayed link
            link = ad.get("link", "")
            displayed_link = ad.get("displayed_link", "")

            # Try to extract domain
            domain = displayed_link or self._extract_domain(link)

            # Build our ad data structure
            ad_data = {
                "keyword": keyword,
                "location": location,
                "device_type": device,
                "advertiser_domain": domain,
                "advertiser_name": ad.get("source", domain),
                "display_url": displayed_link or link,
                "final_url": link,
                "landing_page_url": link,
                "ad_position": position,
                "is_top_ad": is_top,
                "source": "serpapi",
                "raw_data": ad,  # Store original data
                "headlines": [],
                "descriptions": [],
                "extensions": [],
            }

            # Extract title/headline
            if "title" in ad:
                ad_data["headlines"].append({
                    "headline_text": ad["title"],
                    "position": 1
                })

            # Extract description
            if "snippet" in ad:
                ad_data["descriptions"].append({
                    "description_text": ad["snippet"],
                    "position": 1
                })

            # Extract sitelinks (if available)
            if "sitelinks" in ad:
                for idx, sitelink in enumerate(ad["sitelinks"]):
                    if isinstance(sitelink, dict):
                        ad_data["extensions"].append({
                            "extension_type": "sitelink",
                            "extension_text": sitelink.get("title", ""),
                            "extension_url": sitelink.get("link", ""),
                            "position": idx + 1
                        })

            # Extract inline sitelinks
            if "inline_links" in ad:
                for idx, link_data in enumerate(ad["inline_links"]):
                    if isinstance(link_data, dict):
                        ad_data["extensions"].append({
                            "extension_type": "sitelink",
                            "extension_text": link_data.get("title", ""),
                            "extension_url": link_data.get("link", ""),
                            "position": len(ad_data["extensions"]) + 1
                        })

            # Extract callouts (if available)
            if "rich_snippet" in ad and "extensions" in ad["rich_snippet"]:
                for ext in ad["rich_snippet"]["extensions"]:
                    ad_data["extensions"].append({
                        "extension_type": "callout",
                        "extension_text": ext,
                        "position": len(ad_data["extensions"]) + 1
                    })

            return ad_data

        except Exception as e:
            logger.error(f"Error parsing ad: {str(e)}")
            return None

    def _parse_shopping_ad(
        self,
        ad: Dict[str, Any],
        keyword: str,
        location: Optional[str],
        device: str,
        position: int,
    ) -> Optional[Dict[str, Any]]:
        """
        Parse a shopping ad from SerpAPI.
        """
        try:
            link = ad.get("link", "")
            source = ad.get("source", "")

            ad_data = {
                "keyword": keyword,
                "location": location,
                "device_type": device,
                "advertiser_domain": self._extract_domain(link),
                "advertiser_name": source,
                "display_url": link,
                "final_url": link,
                "landing_page_url": link,
                "ad_position": position,
                "is_top_ad": True,
                "source": "serpapi_shopping",
                "raw_data": ad,
                "headlines": [],
                "descriptions": [],
                "extensions": [],
            }

            # Title as headline
            if "title" in ad:
                ad_data["headlines"].append({
                    "headline_text": ad["title"],
                    "position": 1
                })

            # Price and rating as description
            desc_parts = []
            if "price" in ad:
                desc_parts.append(f"Price: {ad['price']}")
            if "rating" in ad:
                desc_parts.append(f"Rating: {ad['rating']}")
            if "reviews" in ad:
                desc_parts.append(f"Reviews: {ad['reviews']}")

            if desc_parts:
                ad_data["descriptions"].append({
                    "description_text": " | ".join(desc_parts),
                    "position": 1
                })

            return ad_data

        except Exception as e:
            logger.error(f"Error parsing shopping ad: {str(e)}")
            return None

    def _extract_domain(self, url: str) -> str:
        """
        Extract domain from URL.
        """
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc or parsed.path
            # Remove www.
            if domain.startswith("www."):
                domain = domain[4:]
            return domain
        except:
            return url

    def test_connection(self) -> bool:
        """
        Test if the API key works.
        """
        try:
            params = {
                "q": "test",
                "api_key": self.api_key,
                "engine": "google",
                "gl": "us",
                "num": 1,
            }
            search = GoogleSearch(params)
            results = search.get_dict()
            return "error" not in results
        except Exception as e:
            logger.error(f"SerpAPI connection test failed: {str(e)}")
            return False
