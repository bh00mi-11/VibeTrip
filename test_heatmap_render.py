import json

with open('backend/ml_artifacts/per_query_metrics.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

heatmap_models = ['Baseline', 'Text', 'Visual(Max)', 'Fusion', 'Image-only']
queries = data['queries']
pq = data['per_query_metrics']

rendered = []
for q in queries:
    qid = q['query_id']
    row = {'query_id': qid, 'query_text': q['query_text']}
    for m in heatmap_models:
        cell = pq.get(m, {}).get(qid, {})
        row[m] = {
            'p5': round(cell.get('p_at_5', 0), 3),
            'ndcg5': round(cell.get('ndcg_at_5', 0), 3),
            'top10_len': len(cell.get('top10', [])),
            'gt_len': len(cell.get('relevant_destinations', []))
        }
    rendered.append(row)

print("=== FIRST 3 RENDERED ROWS IN FRONTEND HEATMAP ===")
for r in rendered[:3]:
    print(f"Query {r['query_id']} ({r['query_text']}):")
    for m in heatmap_models:
        c = r[m]
        print(f"  {m:12s}: P@5 = {c['p5']:.3f} | NDCG@5 = {c['ndcg5']:.3f} | Top10 items = {c['top10_len']} | GT items = {c['gt_len']}")

print("\n=== BASELINE PER-QUERY COMPARISON WITH SOURCE ===")
baseline_expected = {
    "q01": (0.600, 0.684),
    "q02": (0.200, 0.214),
    "q03": (0.600, 0.447),
    "q04": (0.000, 0.000),
    "q05": (0.000, 0.000),
    "q06": (0.000, 0.000),
    "q07": (0.400, 0.485),
    "q08": (0.000, 0.000),
    "q09": (0.800, 0.869),
    "q10": (0.800, 0.830),
    "q11": (0.200, 0.339),
    "q12": (0.200, 0.214)
}

all_match = True
for r in rendered:
    qid = r['query_id']
    actual_p5 = r['Baseline']['p5']
    actual_n5 = r['Baseline']['ndcg5']
    exp_p5, exp_n5 = baseline_expected[qid]
    match = (abs(actual_p5 - exp_p5) < 1e-4) and (abs(actual_n5 - exp_n5) < 1e-4)
    if not match:
        all_match = False
    print(f"  {qid}: P@5 {actual_p5:.3f} (exp {exp_p5:.3f}) / NDCG@5 {actual_n5:.3f} (exp {exp_n5:.3f}) => Match: {match}")

fusion_p5 = [r['Fusion']['p5'] for r in rendered]
fusion_n5 = [r['Fusion']['ndcg5'] for r in rendered]
mean_f_p5 = sum(fusion_p5) / len(fusion_p5)
mean_f_n5 = sum(fusion_n5) / len(fusion_n5)
print(f"\nFusion Mean P@5: {mean_f_p5:.3f} (Target: 0.550) => Match: {abs(mean_f_p5 - 0.550) < 1e-4}")
print(f"Fusion Mean NDCG@5: {mean_f_n5:.3f} (Target: 0.537) => Match: {abs(mean_f_n5 - 0.5374) < 1e-3 or abs(mean_f_n5 - 0.537) < 1e-3}")
print(f"All baseline values match exactly: {all_match}")
