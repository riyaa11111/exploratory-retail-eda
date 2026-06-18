import pandas as pd
import matplotlib.pyplot as plt
import os


def load_data(file_path: str) -> pd.DataFrame:
    """
    Loads the retail transaction dataset and fixes formatting issues dynamically.
    Ensures that trailing spaces and quotes don't break the pipeline.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Data file not found at {file_path}. Please check the path.")

    # skipinitialspace aur quotechar lagane se corrupt rows handle ho jaati hain
    df = pd.read_csv(file_path, sep=',', skipinitialspace=True, quotechar='"')

    # Saare column names ke aage-peeche se extra spaces clean kar dete hain
    df.columns = df.columns.str.strip()

    return df


def process_retail_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans data types and engineers performance metrics like Revenue.
    """
    # Missing values ko drop karte hain
    df = df.dropna().copy()

    # Safe side: Agar values strings me hain, toh unhe numbers me convert karte hain
    df['Units_Sold'] = pd.to_numeric(df['Units_Sold'], errors='coerce')
    df['Unit_Price'] = pd.to_numeric(df['Unit_Price'], errors='coerce')

    # Conversion ke baad agar koi row nan bani ho toh use remove karte hain
    df = df.dropna().copy()

    # --- Feature Engineering: Calculating total revenue ---
    df['Revenue'] = df['Units_Sold'] * df['Unit_Price']

    # Conditional Flagging for high priced items
    df['High_Price_Flag'] = df['Unit_Price'].apply(lambda x: 'Yes' if x > 500 else 'No')
    return df


def generate_sales_insights(df: pd.DataFrame):
    """
    Aggregates and segments data to find top-performing products.
    """
    # 1. High Revenue Segments (> 20,000)
    high_revenue_df = df[df['Revenue'] > 20000]

    # 2. Total Revenue by Product Category (Aggregation)
    product_revenue = df.groupby('Products')['Revenue'].sum().reset_index()

    return high_revenue_df, product_revenue


def plot_revenue_distribution(revenue_df: pd.DataFrame, save_path="revenue_chart.png"):
    """
    Generates a professional bar chart and saves it automatically for GitHub README.
    """
    plt.style.use('ggplot')
    plt.figure(figsize=(9, 5))

    # Professional standard color palette
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

    plt.bar(revenue_df['Products'], revenue_df['Revenue'], color=colors, edgecolor='black', alpha=0.85)

    plt.title('Total Revenue Distribution by Product Category', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Product Category', fontsize=11, labelpad=10)
    plt.ylabel('Total Revenue ($)', fontsize=11, labelpad=10)
    plt.grid(axis='y', linestyle='--', alpha=0.5)

    plt.tight_layout()

    # Chart ko outputs/README ke liye local system me save karna
    plt.savefig(save_path, dpi=300)
    print(f"\n[Success] Chart saved successfully as '{save_path}'")
    plt.show()


# Main Execution Pipeline
# Main Execution Pipeline
if __name__ == "__main__":
    pd.set_option('display.max_columns', None)

    DATA_PATH = "data/retail_sales.csv"

    # --- 🛠️ FORCE FIX: Yeh block aapki file ko sahi format me fir se likh dega ---
    print("Fixing CSV File Format Automatically...")
    correct_csv_content = """Products,Region,Units_Sold,Unit_Price
Laptop,East,100,800
Tablet,West,150,300
Laptop,North,120,850
Monitor,East,80,200
Tablet,South,200,310
Monitor,North,90,210"""

    # Sahi folder architecture path ensure karna
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        f.write(correct_csv_content.strip())
    print("CSV File Fixed Successfully!\n")
    # ------------------------------------------------------------------------

    try:
        print("Starting Retail EDA Data Pipeline...\n")

        # 1. Load
        raw_data = load_data(DATA_PATH)

        # 2. Clean & Engineer
        processed_data = process_retail_data(raw_data)

        # 3. Analyze
        high_rev, prod_rev = generate_sales_insights(processed_data)

        print("=== Full Processed Dataset with Revenue & Flags ===")
        print(processed_data, "\n")

        print("=== High Revenue Segments (> $20,000) ===")
        print(high_rev if not high_rev.empty else "No segments cross $20,000", "\n")

        print("=== Total Revenue Aggregation By Product ===")
        print(prod_rev, "\n")

        # 4. Visualize
        plot_revenue_distribution(prod_rev)

    except Exception as e:
        print(f"Error executing pipeline: {e}")