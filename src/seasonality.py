"""
Seasonality + repeat-cadence priors per top-level category.

month_weights: relative demand by month (1=Jan..12=Dec), used to schedule deals.
repeat: 'repeat' categories (socks, basics) can recur; 'oneoff' (winter coat)
should appear rarely in a single profile's year.

These are stated assumptions -- tune and defend them, don't treat as ground truth.
"""

SEASON = {
    "outerwear":   {"month_weights": {1:1.3,2:1.1,3:.7,4:.5,5:.3,6:.2,7:.2,8:.4,9:.8,10:1.2,11:1.4,12:1.5}, "repeat": "oneoff"},
    "swimwear":    {"month_weights": {1:.3,2:.4,3:.7,4:1.1,5:1.5,6:1.6,7:1.4,8:1.0,9:.5,10:.3,11:.3,12:.4}, "repeat": "oneoff"},
    "footwear":    {"month_weights": {m: 1.0 for m in range(1,13)}, "repeat": "repeat"},
    "upperbody":   {"month_weights": {m: 1.0 for m in range(1,13)}, "repeat": "repeat"},
    "lowerbody":   {"month_weights": {m: 1.0 for m in range(1,13)}, "repeat": "repeat"},
    "fullbody":    {"month_weights": {1:.8,2:.8,3:1.0,4:1.2,5:1.3,6:1.2,7:1.1,8:1.0,9:1.0,10:.9,11:1.0,12:1.4}, "repeat": "oneoff"},
    "lingerie":    {"month_weights": {1:.9,2:1.4,3:.9,4:.9,5:.9,6:.9,7:.9,8:.9,9:.9,10:.9,11:1.0,12:1.4}, "repeat": "repeat"},
    "accessories": {"month_weights": {1:.9,2:.9,3:.9,4:.9,5:.9,6:.9,7:.9,8:.9,9:.9,10:1.0,11:1.3,12:1.6}, "repeat": "repeat"},
    "assorted":    {"month_weights": {m: 1.0 for m in range(1,13)}, "repeat": "repeat"},
}

def week_to_month(week: int) -> int:
    return min(12, max(1, (week - 1) // 4 + 1))
