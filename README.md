# Calculator with Guardrails — Lab Starter (Unit 1)

Your job this week: turn this broken calculator into a safe one.

## What's here

- `calculator.py` — a calculator with **no guardrails**. It crashes on bad input and divides by zero.
- `test_calculator.py` — checks your calculator's behavior. Run it to see how you're doing.
- `README.md` — this file. You'll edit it at the end.

## Your job

Run the calculator first and see it fail:

```bash
python3 calculator.py
```

Then type `hello` when it asks for a number. Then try dividing by zero. Watch it crash — twice.

### Milestone 1 (Friday): basic operations + first guardrail

Fix `calculator.py` so that:

1. **Invalid input** (like `hello`) doesn't crash — it asks again.
2. **Division by zero** doesn't crash — it prints a friendly message instead.
3. The program keeps running until the user chooses to quit.

Use what you learned this week: `input()`, `int()`/`float()`, and `try/except`.

### Stretch (optional)

- Add `%` (remainder) and `**` (power) to the menu.
- Reject numbers that are absurdly large (say, over 10**15) with a warning about overflow.

## Check your progress

```bash
python3 test_calculator.py
```

Each `PASS` is a guardrail working. Your goal for today is at least the first 3 tests passing.

## How to save your work

```bash
git add calculator.py
git commit -m "add input validation guardrail"
git push
```

(Password prompt = Personal Access Token, not your GitHub password.)

## Turn in

Push your final `calculator.py`, then open a Pull Request from your repo back to the original repo
(Contribute → Open pull request). Turn in the PR link on Google Classroom. Due 11:59 PM Friday.