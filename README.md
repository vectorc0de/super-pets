# 🐾 Backend API for Animal Shelter Management (Flask + Supabase) 🏡

This Flask-powered backend provides a comprehensive API for managing an animal shelter's data, including people (clients, contacts) and the adorable pets under their care. It leverages Supabase for its database and storage needs, offering a robust and scalable solution.

## ✨ A Paw-some Overview! 🐶🐱🐰

This backend is the heart of the animal shelter system, providing all the necessary tools to manage people, their furry (and not-so-furry) friends, and all the related information. Think of it as the digital command center for happy tails!

* **👤 People Management:** Add, view, update, and delete information about clients, adopters, and other contacts. Keep track of their details like name, contact information, and address.
* **🐕🐈 Pet Management:** Register new pets with details like name, breed, type, sex, color, background story, and current status. Easily retrieve, modify, and remove pet records.
* **🔗 Powerful Relationships:** Seamlessly link pets to their owners or caretakers, providing a clear connection between people and animals.
* **🖼️ Photo Uploads:** Upload adorable photos of the pets, making their profiles even more engaging.
* **📤 Data Export:** Easily export lists of people and pets for reporting or other purposes.
* **🔒 Secure Authentication:** Ensures that only logged-in clients can access and manage their associated data.
* **☁️ Powered by Supabase:** Utilizes Supabase for a scalable and real-time backend, handling database and storage efficiently.

## 🚀 Getting Started

Ready to unleash the power of this backend? Here's how to get it running:

### 🛠️ Prerequisites

Make sure you have the following installed:

* **Python:** (3.x is highly recommended!) 🐍
* **pip:** (Python package installer) 📦
* **Flask:** (`pip install Flask`) 🥂
* **Flask-CORS:** (`pip install Flask-CORS`) 🌐
* **Supabase Account:** You'll need a Supabase project set up and your API keys handy! 🔑

### ⚙️ Configuration

1.  **Clone the repository (if you have the code on GitHub):**
    ```bash
    git clone https://github.com/vectorc0de/super-pets
    cd super-pets
    ```

2.  **Set up your virtual environment (highly recommended!):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # macOS/Linux
    venv\Scripts\activate  # Windows
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(You might need to create a `requirements.txt` file listing Flask and Flask-CORS if you haven't already.)*

4.  **Configure Supabase:**
    * Make sure you have your Supabase URL and API key.
    * You'll likely need to set these as environment variables or within your Flask application's configuration.

5.  **Run the Flask development server:**
    ```bash
    flask --app your_app_file.py run --debug
    ```
    *(Replace `your_app_file.py` with the name of your main Flask application file.)*

    The backend API should now be running, typically on `http://127.0.0.1:5000/`.

### 🗺️ API Endpoints

Here's a quick overview of the available API endpoints:

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
* **`GET /export/people`**: Export data for all people. 📤👤
* **`GET /export/pets`**: Export data for all pets. 📤🐾

**Remember to check the code for the specific request body and response formats for each endpoint!**

## 🤝 Join the Pack! (Contributing)

We're always looking for ways to make this backend even better! If you have ideas, find bugs, or want to contribute, please:

1.  Fork the repository. 🍴
2.  Create a new branch for your awesome contribution. 🌿
3.  Write your code and tests! ✅
4.  Commit your changes with clear messages. 💬
5.  Push your branch to your fork. 🚀
6.  Submit a pull request. 📤

## 📜 License

GPL v3
