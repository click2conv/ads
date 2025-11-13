#!/usr/bin/env python3
"""
Test script for SerpAPI integration.
Run this to verify your SerpAPI key works and see sample data.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.serpapi_service import SerpAPIService
from app.core.config import settings
import json


def test_serpapi():
    """Test SerpAPI integration"""
    print("=" * 60)
    print("SerpAPI Integration Test")
    print("=" * 60)

    # Check if API key is configured
    if not settings.SERPAPI_KEY or settings.SERPAPI_KEY == "your_serpapi_key_here":
        print("❌ ERROR: SERPAPI_KEY not configured!")
        print("\nPlease set your SerpAPI key in .env file:")
        print("SERPAPI_KEY=your_actual_key_here")
        return False

    print(f"\n✓ API Key configured: {settings.SERPAPI_KEY[:10]}...")

    # Initialize service
    serpapi = SerpAPIService(settings.SERPAPI_KEY)

    # Test connection
    print("\n1. Testing API connection...")
    if serpapi.test_connection():
        print("   ✓ Connection successful!")
    else:
        print("   ❌ Connection failed!")
        return False

    # Test ad search
    print("\n2. Testing ad search for 'running shoes'...")
    try:
        ads = serpapi.search_ads(
            keyword="running shoes",
            location="United States",
            device="desktop"
        )

        print(f"   ✓ Found {len(ads)} ads!")

        if ads:
            print("\n3. Sample ad data:")
            print("-" * 60)
            for i, ad in enumerate(ads[:3], 1):  # Show first 3 ads
                print(f"\n   Ad #{i}:")
                print(f"   Advertiser: {ad.get('advertiser_name', 'N/A')}")
                print(f"   Domain: {ad.get('advertiser_domain', 'N/A')}")
                print(f"   Position: {ad.get('ad_position', 'N/A')}")

                if ad.get('headlines'):
                    print(f"   Headlines:")
                    for h in ad['headlines']:
                        print(f"     - {h['headline_text']}")

                if ad.get('descriptions'):
                    print(f"   Descriptions:")
                    for d in ad['descriptions']:
                        print(f"     - {d['description_text'][:80]}...")

                if ad.get('extensions'):
                    print(f"   Extensions: {len(ad['extensions'])} found")

            print("\n" + "-" * 60)
            print("\n4. Full data sample (first ad):")
            print(json.dumps(ads[0], indent=2, default=str))

        else:
            print("   ⚠ No ads found (this might be normal for some keywords)")

        print("\n" + "=" * 60)
        print("✓ SerpAPI integration test completed successfully!")
        print("=" * 60)
        print("\nYou can now:")
        print("1. Start the application: docker-compose up -d")
        print("2. Add keywords to monitor in the web UI")
        print("3. Ads will be automatically collected hourly")
        return True

    except Exception as e:
        print(f"\n   ❌ Error: {str(e)}")
        print("\nPlease check:")
        print("1. Your SerpAPI key is valid")
        print("2. You have remaining credits on your SerpAPI account")
        print("3. Your internet connection is working")
        return False


if __name__ == "__main__":
    success = test_serpapi()
    sys.exit(0 if success else 1)
