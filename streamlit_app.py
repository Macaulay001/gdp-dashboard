import streamlit as st
import time
from fpdf import FPDF
import base64
from streamlit_option_menu import option_menu
import os
from PIL import Image
import pandas as pd
from datetime import timedelta
import sqlite3
from num2words import num2words

conn = sqlite3.connect("dojmac_global1.db")
c = conn.cursor()

st.set_page_config("DOJMAC GLOBAL ENTERPRISES",
#    page_icon=Image.open('icons.ico'),
#    layout="wide",
#    initial_sidebar_state="expanded",
)

# Create tables if they don't exist
c.execute("""
CREATE TABLE IF NOT EXISTS sales (
    date TEXT, 
    invoice_number TEXT UNIQUE DEFAULT '000000',
    vendor_name TEXT,
    customer_name TEXT,
    particulars TEXT,
    maruwa_special_quantity_owo INTEGER,
    maruwa_special_quantity_pieces INTEGER,
    maruwa_special_total_price REAL,
    maruwa_quantity_owo INTEGER,
    maruwa_quantity_pieces INTEGER,
    maruwa_total_price REAL,
    honda_special_quantity_owo INTEGER,
    honda_special_quantity_pieces INTEGER,
    honda_special_total_price REAL,
    honda_quantity_owo INTEGER,
    honda_quantity_pieces INTEGER,
    honda_total_price REAL,
    bajaj_quantity_owo INTEGER,
    bajaj_quantity_pieces INTEGER,
    bajaj_total_price REAL,
    lagatha_quantity_owo INTEGER,
    lagatha_quantity_pieces INTEGER,
    lagatha_total_price REAL,
    orobo_quantity_owo INTEGER,
    orobo_quantity_pieces INTEGER,
    orobo_total_price REAL,
    total_price REAL
)
""")

c.execute("""
    CREATE TABLE IF NOT EXISTS awo (
        date TEXT,
        vendor_name TEXT,
        details TEXT,
        price REAL,
        quantity_incoming INTEGER,
        quantity_outgoing INTEGER,
        balance REAL,
        rate  REAL
    )
""")

c.execute("""
    CREATE TABLE IF NOT EXISTS vendors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        name TEXT UNIQUE,
        invoice_number TEXT
          
    )
""")

c.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        balance REAL DEFAULT 0.0,
        phone_number TEXT
    )
""")


def create_customer_table(customer_name):
    table_name = customer_name.replace(" ", "_").lower()
    c.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT,
            date TEXT,
            name TEXT,
            phone_number TEXT,
            details TEXT,
            debit REAL,
            credit REAL,
            balance REAL
        )
    """)
    
    conn.commit()


def create_vendor_table(Vendor_name):
    table_name = Vendor_name.replace(" ", "_").lower()
    c.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            date TEXT,
            vendor_name TEXT,
            details TEXT,
            price REAL,
            quantity_incoming INTEGER,
            quantity_outgoing INTEGER,
            balance REAL,
            rate  REAL,
            type TEXT
        )
    """)
    
    conn.commit()

def tools():
    st.header("Tools: Manage Vendors, Goods, Customers, and Invoices")
    tabs = st.tabs(["Vendors", "Goods", "Customers"])

    with tabs[0]:
        st.subheader("Manage Vendors")
        vendor_name = st.text_input("Vendor Name")

        if st.button("Add Vendor"):
            try:
                c.execute("INSERT INTO vendors (name) VALUES (?)", (vendor_name,))
                conn.commit()
                st.success(f"Added vendor: {vendor_name}")

                create_vendor_table(vendor_name)
                table_name = vendor_name.replace(" ", "_").lower()
                c.execute(f"INSERT INTO {table_name} (name) VALUES (?)", (vendor_name,))
                conn.commit()


            except sqlite3.IntegrityError:
                st.error("Vendor already exists!")

        if st.button("Delete Vendor"):
            c.execute("DELETE FROM vendors WHERE name = ?", (vendor_name,))
            conn.commit()
            st.success(f"Deleted vendor: {vendor_name}")

    with tabs[1]:
        st.subheader("Manage Goods")
        st.text("Coming Soon")

    with tabs[2]:
        st.subheader("Manage Customers")
        customer_name = st.text_input("Customer Name")
        customer_balance = st.number_input("Customer Balance", min_value=0.0, format="%.2f", key='customer_balance')
        customer_phone_number = st.text_input("Phone Number")

        if st.button("Add Customer"):
            try:
                c.execute("INSERT INTO customers (name, balance, phone_number) VALUES (?, ?, ?)", (customer_name, customer_balance, customer_phone_number))
                conn.commit()
                create_customer_table(customer_name)
                table_name = customer_name.replace(" ", "_").lower() 
                c.execute(f"INSERT INTO {table_name} (name, phone_number, balance) VALUES (?, ?, ?)",
                  (customer_name, customer_phone_number, customer_balance))
                conn.commit()

                st.success(f"Added customer: {customer_name} and created tracking table.")
            except sqlite3.IntegrityError:
                st.error("Customer already exists!")

        if st.button("Delete Customer"):
            c.execute("DELETE FROM customers WHERE name = ?", (customer_name,))
            conn.commit()
            st.success(f"Deleted customer: {customer_name}")


def view_tables():
    st.header("View and Manage Tables")
    tables = ["sales", "awo", "vendors", "customers"]
    selected_table = st.selectbox("Select Table to View:", tables, index=0)

    if selected_table == "customers":
        c.execute("SELECT name FROM customers ORDER BY name")
        customers = [row[0] for row in c.fetchall()]
        customer_dropdown = st.selectbox("Select Customer Table:", customers, index=0)

        if customer_dropdown:
            table_name = customer_dropdown.replace(" ", "_").lower()
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
            if not df.empty:
                st.dataframe(df)

                row_id = st.number_input("Enter Row ID to Delete:", min_value=1, step=1)
                if st.button("Delete Row"):
                    try:
                        with st.spinner("Deleting row..."):
                            c.execute(f"DELETE FROM {table_name} WHERE id = ?", (row_id,))
                            conn.commit()
                            st.success("Row deleted successfully")
                    except sqlite3.Error as e:
                        st.error(f"Error: {e}")
            else:
                st.info("The selected table is empty.")
    else:
        df = pd.read_sql_query(f"SELECT * FROM {selected_table}", conn)
        if not df.empty:
            st.dataframe(df)

            row_id = st.number_input("Enter Row ID to Delete:", min_value=1, step=1)
            if st.button("Delete Row"):
                try:
                    with st.spinner("Deleting row..."):
                        c.execute(f"DELETE FROM {selected_table} WHERE rowid = ?", (row_id,))
                        conn.commit()
                        st.success("Row deleted successfully")
                except sqlite3.Error as e:
                    st.error(f"Error: {e}")
        else:
            st.info("The selected table is empty.")


def deposit():
    date = st.date_input("Enter Date:")
    date = date.strftime("%Y-%m-%d")

    c.execute("SELECT name FROM customers ORDER BY name")
    customers = [row[0] for row in c.fetchall()]
    selected_customer = st.selectbox("Select Customer", customers)

    details = st.text_area("Details")

    amount = st.number_input("Enter Amount Deposited", min_value=0.0)

    if st.button("Upload"):
        try:
            with st.spinner("Saving..."):
                table_name = selected_customer.replace(" ", "_").lower()
                c.execute(f"SELECT balance FROM {table_name} ORDER BY id DESC LIMIT 1")
                previous_balance = c.fetchone()
                if previous_balance:
                    new_balance = previous_balance[0] + amount
                else:
                    new_balance = -amount


                table_name = selected_customer.replace(" ", "_").lower()
                c.execute(f"INSERT INTO {table_name} (date, details, credit, balance) VALUES (?, ?, ?, ?) ",
                          (date, details, amount, new_balance))
                c.execute("UPDATE customers SET balance = balance + ? WHERE name = ?", (new_balance, selected_customer))
                conn.commit()
                st.success("Deposit recorded successfully")
        except sqlite3.Error as e:
            st.error(f"Error: {e}")



def Sales():
    if 'reset' not in st.session_state:
        st.session_state.reset = False

    # Initialize values
    maruwa_special_quantity1, maruwa_special_quantity2 = 0, 0
    maruwa_quantity1, maruwa_quantity2 = 0, 0
    honda_special_quantity1, honda_special_quantity2 = 0, 0
    honda_quantity1, honda_quantity2 = 0, 0
    bajaj_quantity1, bajaj_quantity2 = 0, 0
    lagatha_quantity1, lagatha_quantity2 = 0, 0
    orobo_quantity1, orobo_quantity2 = 0, 0


    date = st.date_input("Enter Date:")
    date = date.strftime("%Y-%m-%d")

    c.execute("SELECT COALESCE(MAX(CAST(invoice_number AS INTEGER)), 0) + 1 FROM sales")
    invoice_number = str(c.fetchone()[0]).zfill(6)

    c.execute("SELECT name FROM vendors")
    vendors = [row[0] for row in c.fetchall()]
    selected_vendor = st.selectbox("Select Vendor", vendors)

    c.execute("SELECT name FROM customers")
    customers = [row[0] for row in c.fetchall()]
    selected_customer = st.selectbox("Select Customer", customers)

    particulars = st.text_input("Particulars")

    goods = ["Maruwa Special", "Maruwa", "Honda Special", "Honda", "Bajaj", "Lagatha", "Orobo"]
    price1 = [100.0, 16000, 120.0, 100.0, 90.0, 150.0, 200.0]
    price2 = [80.0, 320, 100.0, 80.0, 70.0, 120.0, 150.0]
    selected_goods = st.multiselect("Select Goods:", goods)

    total_price = 0
    if "Maruwa Special" in selected_goods:
        col1, col2 = st.columns(2)
        with col1:
            maruwa_special_quantity1 = st.number_input("Enter Maruwa Special Owo:", min_value=0, key="maruwa_special_quantity1")
        with col2:
            maruwa_special_quantity2 = st.number_input("Enter Maruwa Special Pieces:", min_value=0, key="maruwa_special_quantity2")

        total_price += (maruwa_special_quantity1 * price1[0]) + (maruwa_special_quantity2 * price2[0])

    if "Maruwa" in selected_goods:
        col1, col2 = st.columns(2)
        with col1:
            maruwa_quantity1 = st.number_input("Maruwa Owo (#16000):", min_value=0, key="maruwa_quantity1")
        with col2:
            maruwa_quantity2 = st.number_input("Maruwa Pieces (#320):", min_value=0, key="maruwa_quantity2")

        total_price += (maruwa_quantity1 * price1[1]) + (maruwa_quantity2 * price2[1])

    if "Honda Special" in selected_goods:
        col1, col2 = st.columns(2)
        with col1:
            honda_special_quantity1 = st.number_input("Honda Special Owo:", min_value=0, key="honda_special_quantity1")
        with col2:
            honda_special_quantity2 = st.number_input("Honda Special Pieces:", min_value=0, key="honda_special_quantity2")

        total_price += (honda_special_quantity1 * price1[2]) + (honda_special_quantity2 * price2[2])

    if "Honda" in selected_goods:
        col1, col2 = st.columns(2)
        with col1:
            honda_quantity1 = st.number_input("Honda Owo:", min_value=0, key="honda_quantity1")
        with col2:
            honda_quantity2 = st.number_input("Honda Pieces:", min_value=0, key="honda_quantity2")

        total_price += (honda_quantity1 * price1[3]) + (honda_quantity2 * price2[3])

    if "Bajaj" in selected_goods:
        col1, col2 = st.columns(2)
        with col1:
            bajaj_quantity1 = st.number_input("Bajaj Owo:", min_value=0, key="bajaj_quantity1")
        with col2:
            bajaj_quantity2 = st.number_input("Bajaj Pieces:", min_value=0, key="bajaj_quantity2")

        total_price += (bajaj_quantity1 * price1[4]) + (bajaj_quantity2 * price2[4])

    if "Lagatha" in selected_goods:
        col1, col2 = st.columns(2)
        with col1:
            lagatha_quantity1 = st.number_input("Lagatha Owo:", min_value=0, key="lagatha_quantity1")
        with col2:
            lagatha_quantity2 = st.number_input("Lagatha Pieces:", min_value=0, key="lagatha_quantity2")

        total_price += (lagatha_quantity1 * price1[5]) + (lagatha_quantity2 * price2[5])

    if "Orobo" in selected_goods:
        col1, col2 = st.columns(2)
        with col1:
            orobo_quantity1 = st.number_input("Orobo Owo:", min_value=0, key="orobo_quantity1")
        with col2:
            orobo_quantity2 = st.number_input("Orobo Pieces:", min_value=0, key="orobo_quantity2")

        total_price += (orobo_quantity1 * price1[6]) + (orobo_quantity2 * price2[6])

    st.subheader(f"Total Price: #{total_price:.2f}")
    total_price_in_words = num2words(total_price, lang='en')
    st.subheader(f"Total Price in Words: {total_price_in_words}")

    if st.button("Save Sales"):
        try:
            with st.spinner("Saving..."):
                c.execute("""
                    INSERT INTO sales (
                        date, invoice_number, vendor_name, customer_name, particulars,
                        maruwa_special_quantity_owo, maruwa_special_quantity_pieces, maruwa_special_total_price,
                        maruwa_quantity_owo, maruwa_quantity_pieces, maruwa_total_price,
                        honda_special_quantity_owo, honda_special_quantity_pieces, honda_special_total_price,
                        honda_quantity_owo, honda_quantity_pieces, honda_total_price,
                        bajaj_quantity_owo, bajaj_quantity_pieces, bajaj_total_price,
                        lagatha_quantity_owo, lagatha_quantity_pieces, lagatha_total_price,
                        orobo_quantity_owo, orobo_quantity_pieces, orobo_total_price,
                        total_price
                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, (
                    date, invoice_number, selected_vendor, selected_customer, particulars,
                    maruwa_special_quantity1, maruwa_special_quantity2, (maruwa_special_quantity1 * price1[0]) + (maruwa_special_quantity2 * price2[0]),
                    maruwa_quantity1, maruwa_quantity2, (maruwa_quantity1 * price1[1]) + (maruwa_quantity2 * price2[1]),
                    honda_special_quantity1, honda_special_quantity2, (honda_special_quantity1 * price1[2]) + (honda_special_quantity2 * price2[2]),
                    honda_quantity1, honda_quantity2, (honda_quantity1 * price1[3]) + (honda_quantity2 * price2[3]),
                    bajaj_quantity1, bajaj_quantity2, (bajaj_quantity1 * price1[4]) + (bajaj_quantity2 * price2[4]),
                    lagatha_quantity1, lagatha_quantity2, (lagatha_quantity1 * price1[5]) + (lagatha_quantity2 * price2[5]),
                    orobo_quantity1, orobo_quantity2, (orobo_quantity1 * price1[6]) + (orobo_quantity2 * price2[6]),
                    total_price
                ))
                conn.commit()

                # Insert into customer's account

                #custom_particulars, make a statement with goods > 0 by reading the db
                particulars = ""
                if maruwa_special_quantity1 > 0 or maruwa_special_quantity2 > 0:
                    particulars += f"Maruwa Special: {maruwa_special_quantity1} Owo, {maruwa_special_quantity2} Pieces\n"
                if maruwa_quantity1 > 0 or maruwa_quantity2 > 0:
                    particulars += f"Maruwa: {maruwa_quantity1} Owo, {maruwa_quantity2} Pieces\n"
                if honda_special_quantity1 > 0 or honda_special_quantity2 > 0:
                    particulars += f"Honda Special: {honda_special_quantity1} Owo, {honda_special_quantity2} Pieces\n"
                if honda_quantity1 > 0 or honda_quantity2 > 0:
                    particulars += f"Honda: {honda_quantity1} Owo, {honda_quantity2} Pieces\n"
                if bajaj_quantity1 > 0 or bajaj_quantity2 > 0:
                    particulars += f"Bajaj: {bajaj_quantity1} Owo, {bajaj_quantity2} Pieces\n"
                if lagatha_quantity1 > 0 or lagatha_quantity2 > 0:
                    particulars += f"Lagatha: {lagatha_quantity1} Owo, {lagatha_quantity2} Pieces\n"
                if orobo_quantity1 > 0 or orobo_quantity2 > 0:
                    particulars += f"Orobo: {orobo_quantity1} Owo, {orobo_quantity2} Pieces\n"

                

                table_name = selected_customer.replace(" ", "_").lower()
                c.execute(f"SELECT balance FROM {table_name} ORDER BY id DESC LIMIT 1")
                previous_balance = c.fetchone()
                if previous_balance:
                    new_balance = previous_balance[0] - total_price
                else:
                    new_balance = -total_price

                c.execute(f"INSERT INTO {table_name} (date, invoice_number, details, debit, balance) VALUES (?, ?, ?, ?, ?) ",
                          (date, invoice_number, particulars, total_price, new_balance))
                c.execute("UPDATE customers SET balance = ? WHERE name = ?", (new_balance, selected_customer))
                conn.commit()


                st.balloons()
        except sqlite3.IntegrityError:
            st.error("Invoice already exists!")


def awo():
    date = st.date_input("Enter Date:")
    date = date.strftime("%Y-%m-%d")

    c.execute("SELECT name FROM vendors")
    vendors = [row[0] for row in c.fetchall()]
    selected_vendor = st.selectbox("Select Vendor", vendors)

    details = st.text_area("Details")
    choice = st.selectbox("Select Type:", ["RECEIVED", "PROCESSED"])

    if choice == "RECEIVED":
        quantity = st.number_input("Enter Quantity Received", min_value=0)
        price = st.number_input("Enter Total Price", min_value=0)
        #manage division by zero
        if price > 0:
            rate = price / quantity
        else:
            rate = 0
        if st.button("Check Rate"):
            rate = price / quantity
            st.success(f"Rate: #{rate:.2f} per AWO")
    if choice == "PROCESSED":
        quantity = st.number_input("Enter Quantity Processed", min_value=0)

    if st.button("Upload"):
        try:
            with st.spinner("Saving..."):
                
                if choice == "RECEIVED":
                    table_name = selected_vendor.replace(" ", "_").lower()
                    c.execute(f"INSERT INTO {table_name} (date, vendor_name, details, quantity_incoming, price, rate, type, balance) VALUES (?,?,?,?,?,?,?,?)",
                              (date, selected_vendor, details, quantity, price, rate, "incoming", quantity))

                elif choice == "PROCESSED":
                    c.execute(f"INSERT INTO {table_name} (date, vendor_name, details, quantity_outgoing) VALUES (?, ?, ?, ?)",
                              (date, selected_vendor, details, quantity))
                conn.commit()
                st.success("Uploaded successfully")
        except sqlite3.Error as e:
            st.error(f"Error: {e}")



selected = option_menu(
    menu_title=None,
    options=["Sales", "AWO", "Deposit", "Tools", "View Tables"],
    icons=["house", "bi bi-person-lock", "bi bi-cash", 'bi bi-tools', 'bi bi-table'],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
)

if selected == "Sales":
    Sales()
elif selected == "AWO":
    awo()
elif selected == "Deposit":
    deposit()
elif selected == "Tools":
    tools()
elif selected == "View Tables":
    view_tables()
