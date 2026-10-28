import urllib.request
import json
import sys

def run_suite():
    print("=" * 80)
    print("VIBETRIP RECOMMENDATION SYSTEM COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    
    test_cases = [
        {
            "name": "TEST 1: User Screenshot Filter Combination (Adventure=High, Visual=High, Nature=Med, Peace=Med, Crowd=Med)",
            "payload": {
                "target_dims": {
                    "nature": "medium",
                    "adventure": "high",
                    "peacefulness": "medium",
                    "crowd_match": "medium",
                    "visual_atmosphere": "high"
                },
                "query_text": ""
            },
            "should_include_top": ["Goa", "Rishikesh"],
            "must_not_include_top": ["Jodhpur", "Udaipur", "Agra", "Delhi"]
        },
        {
            "name": "TEST 2: Extreme Outdoor Adventure (Adventure=High, Nature=High, Peace=Med, Crowd=Med, Visual=High)",
            "payload": {
                "target_dims": {
                    "nature": "high",
                    "adventure": "high",
                    "peacefulness": "medium",
                    "crowd_match": "medium",
                    "visual_atmosphere": "high"
                },
                "query_text": ""
            },
            "should_include_top": ["Leh", "Goa", "Manali"],
            "must_not_include_top": ["Varanasi", "Amritsar", "Agra", "Delhi", "Jodhpur"]
        },
        {
            "name": "TEST 3: Spiritual & Heritage Exploration (Nature=Med, Adventure=Low, Peace=High, Crowd=Med, Visual=High)",
            "payload": {
                "target_dims": {
                    "nature": "medium",
                    "adventure": "low",
                    "peacefulness": "high",
                    "crowd_match": "medium",
                    "visual_atmosphere": "high"
                },
                "query_text": ""
            },
            "should_include_top": ["Udaipur", "Khajuraho", "Bodh Gaya"],
            "must_not_include_top": ["Rishikesh", "Manali", "Leh", "Goa"]
        },
        {
            "name": "TEST 4: Direct Semantic Keyword Search for Rafting & Bungee",
            "payload": {
                "target_dims": {
                    "nature": "medium",
                    "adventure": "high",
                    "peacefulness": "medium",
                    "crowd_match": "medium",
                    "visual_atmosphere": "high"
                },
                "query_text": "white water river rafting and bungee jumping"
            },
            "should_include_top": ["Rishikesh"],
            "must_not_include_top": ["Agra", "Delhi"]
        }
    ]

    all_passed = True
    
    for tc in test_cases:
        print(f"\n[RUNNING] {tc['name']}")
        req = urllib.request.Request(
            'http://127.0.0.1:8005/api/recommend',
            data=json.dumps(tc['payload']).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        try:
            res = urllib.request.urlopen(req)
            data = json.loads(res.read())
            recs = data.get('recommendations', [])
            top_5_names = [r['name'] for r in recs[:5]]
            
            print(f"  Top 5 returned: {top_5_names}")
            for r in recs[:5]:
                print(f"    - {r['name']:20} | Fit: {r['overall_match_score']:5.1f}% | Adv: {r['scores']['adventure']:4.1f} | Nat: {r['scores']['nature']:4.1f} | Vis: {r['scores']['visual_atmosphere']:4.1f} | Peace: {r['scores']['peacefulness']:4.1f}")

            # Assertions
            passed = True
            for expected in tc['should_include_top']:
                if expected not in top_5_names:
                    print(f"  [FAIL]: Expected '{expected}' in top 5, but got {top_5_names}")
                    passed = False
            for forbidden in tc['must_not_include_top']:
                if forbidden in [recs[0]['name'], recs[1]['name']]:
                    print(f"  [FAIL]: Forbidden mismatch spot '{forbidden}' ranked at the top!")
                    passed = False
                    
            if passed:
                print(f"  [PASS]: {tc['name']} PASSED.")
            else:
                all_passed = False
                
        except Exception as e:
            print(f"  [ERROR] executing test: {e}")
            all_passed = False

    print("\n" + "=" * 80)
    if all_passed:
        print("ALL TESTS PASSED! Recommendation system is consistent, accurate, and constraint-respecting.")
    else:
        print("SOME TESTS FAILED! Check logic.")
    print("=" * 80)
    return all_passed

if __name__ == '__main__':
    success = run_suite()
    sys.exit(0 if success else 1)
