# med-expiry-tracker

A Python CLI that tracks a home medicine cabinet: add medicines with expiry
dates, and check for expired / soon-to-expire items with storage tips.

> ⚠️ **Educational/demo only — not medical advice.** Never take an expired
> medicine; when in doubt, ask a pharmacist.

## Run

```bash
python tracker.py demo                                  # seed demo cabinet + full check
python tracker.py add "Paracetamol 500mg" 2027-03-01 --qty 20
python tracker.py list
python tracker.py check                                 # 30/90-day warning windows
python tracker.py remove "Paracetamol 500mg"
python -m unittest discover -s tests -v
```

## Check output

Expired items are flagged for safe disposal, items expiring within 30 days are
flagged to use first / replace soon, and items within 90 days are listed to
watch. Storage tips (room / cool-dry / fridge) are included per item type.

## Author

M.Muhamad Ashik — Founder, Prescripsy · Contact: prescripsy@prescripsy.space

## License

MIT — see `LICENSE`.
