# **Rentora: Local Market, Reimagined**

Rentora is a decentralized marketplace designed to connect users within local communities for renting and selling items. Powered by the uAgents framework, Rentora provides secure OTP-protected transactions and a user-friendly interface built with Tkinter.

## **Features**

- **Local Marketplace**: Rent or sell items in your neighborhood with ease.
- **Secure Transactions**: OTP-secured payments ensure a trusted environment.
- **Decentralized Architecture**: Powered by uAgents framework for scalability.
- **Wallet System**: Simple and automatic payment handling for smooth transactions.
- **User-Friendly Interface**: Easy-to-navigate Tkinter-based UI for all users.

## **Getting Started**

### **Prerequisites**

- Python 3.x
- Tkinter (included with Python)
- Fetch.ai uAgents framework

### **Installation**

1. **Clone the repository:**

   ```bash
   git clone https://github.com/krishnakumbhaj/Rentora.git
   cd rentora
   ```

2. **Setting up environment:**

    ```bash
    python -m venv env
    source env/Scripts/activate
    ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**

   ```bash
   python central.py
   python city.py # As many cities you would like to add
   python users.py # As many users you would like to add
   python ui.py # For Accessing the Application
   ```

## **How It Works**

1. **Connect to a Local Agent**: Users select their location and connect to the nearest local agent via a central agent.
2. **List Items**: Easily list items for rent or sale, or browse items available locally.
3. **OTP-Secured Transactions**: Complete transactions with one-time password (OTP) security for peace of mind.
4. **Payment Handling**: All payments are managed through the built-in wallet system.

## **Usage**

1. **Listing Items**:  
   - Go to the "List an Item" section and fill in the required details (item name, price, etc.).
   - Confirm the listing, and it will be visible to users in your local area.

2. **Renting or Buying**:  
   - Browse available listings by category or search for specific items.
   - Initiate a transaction and follow the OTP verification process to complete the purchase or rental.

## **Presentation & Resources**

- **Presentation**: [Rentora PPT](https://fetch-a-thon.my.canva.site/rentora)
- **GitHub Repository**: [Rentora Repo](https://github.com/krishnakumbhaj/Rentora)
[![Rentora Demo Video](https://img.youtube.com/vi/BOYW9prw0eY/0.jpg)](https://youtu.be/BOYW9prw0eY)

## **Business Model**

- **Commission**: A small fee is taken from each transaction.
- **Premium Listings**: Users can pay for featured item listings.
- **Subscription Plans**: Frequent users can subscribe for lower transaction fees and extra benefits.

## **Contributing**

We welcome contributions to improve Rentora. Please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a Pull Request.

## **License**

This project is licensed under the MIT License.

## **Warning**

Please note that Rentora is currently under development and is expected to be completed by October 14th, 2024. We kindly ask for your patience and understanding during this period. Thank you for your support!
