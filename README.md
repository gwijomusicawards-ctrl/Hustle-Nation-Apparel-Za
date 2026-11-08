# HUSTLE NATION — Online Store

A Flask + SQLite e-commerce website with customer accounts, creator dashboard, product inventory, image uploads, gallery, maintenance mode, WhatsApp checkout and a browser-based 60-second category advert creator.

## Run locally
1. Install Python 3.11 or newer.
2. Open a terminal in this folder.
3. Run `pip install -r requirements.txt`
4. Set creator credentials before starting:
   - `ADMIN_NAME=Otsile`
   - `ADMIN_PHONE=your-private-creator-phone`
   - `SECRET_KEY=a-long-random-secret`
5. Run `python app.py` and open `http://127.0.0.1:5000`.

On Windows PowerShell, set variables with `$env:ADMIN_NAME="Otsile"` etc. On Android/Pydroid, install requirements and run `app.py`.

## Deploy to GitHub + Render
1. Upload the complete contents of this folder to a GitHub repository.
2. In Render choose **New + → Blueprint**, connect the repository and select `render.yaml`.
3. Set `ADMIN_PHONE` to a private phone number you control. Keep it private.
4. Deploy. The `render.yaml` disk is mounted for the SQLite database and uploaded product/gallery images. If your Render plan does not support persistent disks, use a paid persistent disk or an external database/object storage before accepting real customer orders.
5. Visit `/creator` to open the creator dashboard.

## Creator dashboard
- Add/edit/delete products and update prices, stock, sizes, colours and product images.
- Upload gallery images.
- Edit About Us, Terms, launch notice, WhatsApp and social details.
- Change logo, loader logo, colour theme and maintenance mode.
- Create 60-second category advert videos. The browser records a WebM video; use a browser that supports MediaRecorder (Chrome is recommended).

## Initial creator access
Default creator name is `Otsile`. The default phone value is `0698881104` for first local testing. Set a private `ADMIN_PHONE` in Render before making the store public. Name + phone alone is convenient but is not strong authentication; for a public production store, add a private password or multi-factor protection.

## Customer accounts and privacy
Customers register with name, email, South African ID number, street and password. They log in using email + password; no OTP is used. ID number is collected for account records and is not used as a password. Restrict access to the database and configure backups and a privacy notice before collecting real customer ID data. Consider removing the ID field if it is not necessary for your business.

## WhatsApp checkout
The price list contact `069 888 1104` is preconfigured as `27698881104` for WhatsApp. Customers add products to the bag, log in and press WhatsApp checkout. The order is saved and the WhatsApp message is prefilled. The team must confirm sizes, colours, stock, delivery and payment.

## Price list loaded
- Mind Full of Money Design: Hoodies R350; Sweatshirts R300; T-Shirts R300; Sweatpants R200; Panel Caps R130.
- Young Money Design: Hoodies R350; Sweatshirts R300; T-Shirts R200; Sweatpants R200.
- Classic Design: Hoodies R350; Sweatshirts R300; T-Shirts R300; Sweatpants R200; Panel Caps R130.
- Boys Club and Girls Club Design: Hoodies R380; Sweatshirts R350; T-Shirts R250; Sweatpants R220; Girls Crop Tops R200.
- Newspaper Design: Hoodies R380; Sweatshirts R350; T-Shirts R250; Sweatpants R220.
- Only Cure for the Struggle Design: Hoodies R380; Sweatshirts R350; T-Shirts R250; Sweatpants R220.
- HN Design: Hooded R400; Sweatshirts R350; T-Shirts R250; Sweatpants R220.
- Classic Edition Design: Hoodies R400; Sweatshirts R350; T-Shirts R250; Sweatpants R220; Panel Caps R150.
- Hustle Nation Accessories: Beanies R100; Gloves R100; School Bag R300.
- Mafia Tracksuits: Full Zip Mafia Top R500; Mafia Pants R400; Mafia Shorts R200; 2-Piece Mafia R900.
- 2nd Edition Mafia (not yet released): Mafia Top R550; Mafia Trackpants R450; Mafia Shorts R300; 2-Piece Mafia R1000; Mafia Top and Shorts Set R600.

## Important production notes
This is a deployable starter application, not a fully audited enterprise platform. Before public launch, use HTTPS, configure private credentials, add CSRF protection, rate limiting, privacy/POPIA notices and a proper production database/object storage strategy. Product stock is displayed and managed, but checkout is a WhatsApp enquiry and does not take online card payments or reserve stock automatically. The built-in chatbot is a rule-based store helper, not a connected generative AI service.
