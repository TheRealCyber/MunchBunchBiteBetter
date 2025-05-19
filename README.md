# MunchBunchBiteBetter

### Scan Smart. Eat Right. Powered by AI.

MunchBunchBiteBetter is a smart, user-friendly food and nutrition app designed to simplify dietary decision-making through barcode scanning, personalized recommendations, and AI-powered health scoring. Built with the vision of making healthy eating accessible for all—especially for those with chronic illnesses, the elderly, and fitness-conscious individuals.

---

## Key Features

- Product Barcode Scanning: Scan any product to get instant nutritional details via our database and OpenFoodFacts API.
- Gemini AI Chatbot: Integrated chatbot (via Google Gemini API) to answer queries related to ingredients, food products, and nutritional impact.
- Personalized Recommendations: Tailored food suggestions based on your health profile and dietary goals.
- Health Form Input: Users input age, health goals, dietary restrictions, chronic illnesses, and more for better customization.
- Shopping/Wish List: Manage your grocery list and track whether products are goal-friendly or not.
- Nutrition Grades & Health Scores: Products graded A to E and also tagged as healthy/average/unhealthy via ML models.
- Goal-Friendly Classification: Classifies food items based on whether they support health goals like weight loss, muscle gain, etc.
- Nutritional Summary: View calories, protein, fat, sugar, fiber, and more—per product or in total.
- Admin Dashboard: Manage users, products, and optimize recommendations.
- Light/Dark Mode: Easy-to-navigate UI/UX especially designed for elderly users.

---

## Machine Learning Models

| Task                          | ML Technique                  |
|------------------------------|-------------------------------|
| Personalized Recommendation | SVM (Support Vector Machine)  |
| Health Rating Prediction     | Linear Regression             |
| Health Category Classification | K-means/Hierarchical Clustering |
| Goal-Friendly Tagging        | Clustering based on user goal & product nutrition |

---

## Tech Stack

| Layer     | Tech                  |
|-----------|-----------------------|
| Frontend  | HTML, CSS, JavaScript |
| Backend   | Python Flask          |
| Database  | SQLite                |
| External APIs | OpenFoodFacts, Gemini AI |
| ML Libraries | scikit-learn, pandas, numpy |

---

## Installation & Setup

1. Clone the repository  
   git clone https://github.com/TheRealCyber/MunchBunchBiteBetter.git
   cd MunchBunchBiteBetter

2. Install dependencies  
   pip install -r requirements.txt

3. Run the app  
   python app.py

4. Access the app  
   Open http://localhost:5000 in your browser.

---

## Contributors

- Saloni Sivakumar 
- Aneesh Mathur 
- Mansa Mohanty 

Institution: MPSTME, NMIMS Mumbai Campus  
Department: Computer Engineering (CSBS - 3rd Year)

---

## Motivation

With India’s growing youth population and rising health concerns like diabetes and PCOS, this project aims to empower people to take control of their diet, especially considering India's complex dietary habits (vegetarianism, lactose intolerance, meat-restriction days).

---

## License

This project is licensed under the MIT License.

---

## Contact

Got suggestions, feedback, or want to contribute?  
Drop a message or raise an issue on the GitHub repo!

---

“Let food be thy medicine and medicine be thy food.” – Hippocrates
