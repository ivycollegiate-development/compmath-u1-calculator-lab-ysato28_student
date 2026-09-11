"""Calculator with Guardrails — Lab Starter.

This calculator WORKS but has NO GUARDRAILS.
Your job: make it survive bad input and division by zero.
"""

MENU = """
Choose an operation:
  1) add (+)
  2) subtract (-)
  3) multiply (*)
  4) divide (/)
  q) quit
"""


def get_number(prompt):
    """Ask the user for a number.

    BUG: if the user types something that is not a number,
    float() raises ValueError and the whole program crashes.
    FIX ME: wrap this in try/except so bad input asks again.
    """
    raw = input(prompt)
    return float(raw)


def divide(a, b):
    """Return a / b.

    BUG: ZeroDivisionError if b == 0.
    FIX ME: handle b == 0 safely — return None and let the caller
    print a friendly message, or raise ValueError with a clear message.
    """
    return a / b


def main():
    print("=== Calculator v0 (no guardrails) ===")
    while True:
        print(MENU)
        choice = input("> ").strip().lower()

        if choice == "q":
            print("Goodbye!")
            break

        if choice not in ("1", "2", "3", "4"):
            print("Please pick 1, 2, 3, 4, or q.")
            continue

        a = get_number("First number: ")
        b = get_number("Second number: ")

        if choice == "1":
            result = a + b
        elif choice == "2":
            result = a - b
        elif choice == "3":
            result = a * b
        elif choice == "4":
            result = divide(a, b)

        print(f"Result: {result}")


if __name__ == "__main__":
    main()