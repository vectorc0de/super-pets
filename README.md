# 🐾 Backend API for Animal Shelter Management (Flask + Supabase + Stripe + OpenAI) 🏡

This Flask-powered backend provides a comprehensive API for managing an animal shelter's data, including people (clients, contacts) and the adorable pets under their care. It leverages Supabase for its database and storage needs, **Stripe for payment processing**, and **OpenAI for intelligent data handling**, offering a robust and innovative solution.

## ✨ ¡Un Vistazo Perruno con Inteligencia! 🐶🐱🐰🤖💳

This backend is the intelligent heart of the animal shelter system, providing all the necessary tools to manage people, their furry (and not-so-furry) friends, and related information, now with added superpowers!

* **👤 Gestión de Personas:** Add, view, update, and delete information about clients, adopters, and other contacts. Keep track of their details like name, contact information, and address.
* **🐕🐈 Gestión de Mascotas:** Register new pets with details like name, breed, type, sex, color, background story, and current status. Easily retrieve, modify, and remove pet records.
* **🔗 Relaciones Poderosas:** Seamlessly link pets to their owners or caretakers, providing a clear connection between people and animals.
* **🖼️ Subida de Fotos:** Upload adorable photos of the pets, making their profiles even more engaging.
* **📤 Exportación de Datos:** Easily export lists of people and pets for reporting or other purposes.
* **🤖 Inteligencia Artificial con OpenAI:** **Intelligently processes uploaded CSV files for both people and pets using OpenAI's GPT models.** This includes data formatting and handling potential inconsistencies.
* **💳 Soporte para Stripe:** **Integrates with Stripe for handling donations, adoption fees, or other payment functionalities**, streamlining financial transactions.
* **🔒 Autenticación Segura:** Ensures that only logged-in clients can access and manage their associated data.
* **☁️ Potenciado por Supabase:** Utilizes Supabase for a scalable and real-time backend, handling database and storage efficiently.

## 🚀 ¡Manos a la Obra con Inteligencia! (Getting Started)

Ready to unleash the intelligent power of this backend? Here's how to get it running:

### 🛠️ Requisitos (Prerequisites)

Make sure you have the following installed and set up:

* **Python:** (3.x is highly recommended!) 🐍
* **pip:** (Python package installer) 📦
* **Flask:** (`pip install Flask`) 🥂
* **Flask-CORS:** (`pip install Flask-CORS`) 🌐
* **Supabase Account:** You'll need a Supabase project set up and your API keys handy! 🔑
* **Stripe Account:** Set up a Stripe account and obtain your API keys. 💳
* **OpenAI API Key:** You'll need an API key from OpenAI to utilize the intelligent data processing features. 🤖🔑

### ⚙️ Configuración (Configuration)

1.  **Clone the repository (if you have the code on GitHub):**
    ```bash
    git clone https://github.com/vectorc0de/super-pets
    cd super-pets
    ```

2.  **Set up your virtual environment (¡altamente recomendado!):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # macOS/Linux
    venv\Scripts\activate  # Windows
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Make sure your `requirements.txt` includes `Flask`, `Flask-CORS`, `supabase-py`, `openai`, and `stripe`.)*

4.  **Configure Supabase, Stripe, and OpenAI:**
    * Set your Supabase URL and API key as environment variables or within your Flask application's configuration.
    * Set your Stripe Secret Key as an environment variable or within your Flask application's configuration.
    * Set your OpenAI API Key as an environment variable or within your Flask application's configuration.

5.  **Run the Flask development server:**
    ```bash
    flask --app your_app_file.py run --debug
    ```
    *(Replace `your_app_file.py` with the name of your main Flask application file.)*

    The backend API should now be running, typically on `http://127.0.0.1:5000/`.

### 🗺️ Rutas de la API (API Endpoints)

Here's an updated overview of the available API endpoints:

* **`GET /people`**: Retrieve all people associated with the logged-in client. 👤
* **`GET /person/<uuid:person_id>/pets`**: Get all pets belonging to a specific person. 🐾
* **`GET /pets`**: Retrieve all pets associated with the logged-in client. 🐕🐈🐰
* **`GET /person/<uuid:person_id>`**: Get details for a specific person. 👤🔍
* **`GET /pet/<uuid:pet_id>`**: Get details for a specific pet. 🐾🔍
* **`POST /add_person`**: Add a new person. ➕👤
* **`POST /add_pet`**: Add a new pet (supports photo upload!). ➕🐶
* **`DELETE /delete_person/<uuid:person_id>`**: Delete a specific person. 🗑️👤
* **`DELETE /delete_pet/<uuid:pet_id>`**: Delete a specific pet. 🗑️🐾
* **`POST /upload_photo`**: Upload a photo for a pet. ⬆️🖼️
* **`PUT /pet/<uuid:pet_id>`**: Update information for a specific pet. 📝🐾
* **`PUT /person/<uuid:person_id>`**: Update information for a specific person. 📝👤
* **`POST /upload/pets_csv`**: **Intelligently process a CSV file to add multiple pets using OpenAI.** 🤖➕🐾
* **`POST /upload/people_csv`**: **Intelligently process a CSV file to add multiple people using OpenAI.** 🤖➕👤
* **`GET /export/people`**: Export data for all people. 📤👤
* **`GET /export/pets`**: Export data for all pets. 📤🐾
* **`/stripe/...`**: **Endpoints related to Stripe for handling payments (implementation details not shown in the provided code).** 💳💰

**Remember to check the code for the specific request body and response formats for each endpoint!**

## 🤖 Inteligencia Perruna (AI-Powered Features)

This backend leverages the power of OpenAI to streamline data import:

* **Intelligent CSV Processing:** Upload CSV files containing pet or people data, and the backend uses GPT models to understand and format the data, even with minor inconsistencies or missing columns.
* **Data Normalization:** Automatically attempts to normalize data fields like sex and gender for consistency.

## 💳 ¡Apoya el Refugio! (Stripe Integration)

The backend includes support for Stripe, allowing you to implement features such as:

* **Donations:** Enable users to easily donate to support the shelter's work.
* **Adoption Fees:** Process payments for pet adoptions.
* **Other Payments:** Handle any other financial transactions related to the shelter.

**(Note: The specific Stripe API endpoints and implementation details would be within your application code, likely in a separate Blueprint or module.)**

## 🤝 ¡Únete a la Manada Inteligente! (Contributing)

We're always looking for ways to make this backend even smarter and more helpful! If you have ideas, find bugs, or want to contribute, especially with improving the AI integration or Stripe functionality, please:

1.  Fork the repository. 🍴
2.  Create a new branch for your awesome contribution. 🌿
3.  Write your code and tests! ✅
4.  Commit your changes with clear messages. 💬
5.  Push your branch to your fork. 🚀
6.  Submit a pull request. 📤

## 📜 Licencia (License)

[Add your license here! For example: MIT License] 📝

---

This backend is taking animal shelter management to the next level with the power of AI and seamless payment processing! We hope you find it incredibly useful! If you have any questions, don't hesitate to bark, meow, or even ask an AI! 😉 Greetings from a sunny morning in Barcelona, Anzoátegui! ☀️