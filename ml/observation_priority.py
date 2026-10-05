import sys
import json


try:
    raw_input = sys.stdin.read()

    if not raw_input.strip():
        raise ValueError("No input data received.")

    data = json.loads(raw_input)

    results = data["results"]

    priority_results = []

    for item in results:

        uncertainty = float(item["uncertainty"])

        # Convert uncertainty into a 0-100 priority score
        priority_score = min(
            100,
            uncertainty / 1.5 * 100
        )

        if priority_score >= 70:
            priority = "HIGH"
            recommendation = "Additional in-situ observation recommended"

        elif priority_score >= 30:
            priority = "MEDIUM"
            recommendation = "Monitor with additional observations if available"

        else:
            priority = "LOW"
            recommendation = "Current satellite-based prediction is relatively stable"

        priority_results.append({
            "depth": item["depth"],
            "temperature": item["temperature"],
            "uncertainty": item["uncertainty"],
            "confidence": item["confidence"],
            "priority_score": round(priority_score, 1),
            "priority": priority,
            "recommendation": recommendation
        })

    # Find the highest-priority depth
    highest_priority = max(
        priority_results,
        key=lambda x: x["priority_score"]
    )

    print(json.dumps({
        "success": True,
        "results": priority_results,
        "highest_priority_depth": highest_priority["depth"],
        "highest_priority_score": highest_priority["priority_score"]
    }))


except Exception as error:

    print(json.dumps({
        "success": False,
        "error": str(error)
    }))

    sys.exit(1)