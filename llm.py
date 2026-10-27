import ollama


def analyze_bill(
    bill_data,
    appliances=None,
    estimated_units=None
):
    # -----------------------------
    # Bill Details
    # -----------------------------

    consumer = bill_data.get("Consumer Number", "Not Available")
    date = bill_data.get("Bill Date", "Not Available")
    units = bill_data.get("Units", "Not Available")
    amount = bill_data.get("Amount", bill_data.get("Total Amount", "Not Available"))

    # -----------------------------
    # Appliance Details
    # -----------------------------

    appliance_text = "No appliance information provided."

    if appliances:

        appliance_text = ""

        for item in appliances:

            appliance_text += (
                f"- {item['name']} | "
                f"{item['watts']} W | "
                f"Quantity: {item['quantity']} | "
                f"{item['hours']} hrs/day | "
                f"Estimated Monthly Units: {item['monthly_units']:.2f} kWh\n"
            )

    if estimated_units is None:
        estimated_units = "Not Available"

    # -----------------------------
    # Prompt
    # -----------------------------

    prompt = f"""
You are VOLTWise AI, an expert electricity and energy advisor.

Analyze the following household electricity data.

=========================
ELECTRICITY BILL
=========================

Consumer Number : {consumer}

Bill Date : {date}

Units Consumed : {units}

Bill Amount : ₹{amount}

=========================
HOME APPLIANCES
=========================

{appliance_text}

Estimated Monthly Consumption : {estimated_units}

=========================
YOUR TASK
=========================

Provide a detailed report containing:

1. Overall electricity usage analysis.

2. Whether the bill appears LOW, NORMAL or HIGH.

3. Compare the estimated appliance consumption with the bill (if appliance data is available).

4. Identify which appliances are likely consuming the most electricity.

5. Suggest practical ways to reduce electricity usage.

6. Recommend energy-efficient alternatives where appropriate.

7. Estimate possible monthly savings.

8. Give an Energy Efficiency Score out of 10.

9. End with a short conclusion.

Respond in clear bullet points with simple language.
"""

    # -----------------------------
    # Call Gemma
    # -----------------------------

    try:
        response = ollama.chat(
            model="gemma3:1b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
    except Exception as exc:
        return (
            "Bill analysis could not be completed automatically because the local Ollama "
            f"service is unavailable. Details: {exc}"
        )

    return response["message"]["content"]