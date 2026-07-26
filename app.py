from flask import Flask, request, render_template_string
from datetime import datetime, timedelta
import imaplib
import email
import traceback
import re
import os
import requests
from bs4 import BeautifulSoup
from flask import redirect

app = Flask(__name__)

IMAP_HOST = "mail.mantapnet.com"
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")
ADMIN_PASS = os.environ.get("ADMIN_PASS")
# ADMIN_EMAIL = "admin@mantapnet.com"
# ADMIN_PASS = "fg#$Teds234"
SUBJECTS = {
    "household": [
        "Temporary Access Code",
        "Kod akses sementara"
    ],
    "signin": [
        "Netflix: Your sign-in code",
        "Netflix: Kod daftar masuk anda"
    ],
    "verification": [
        "Your verification code",
        "Kod pengesahan anda"
    ]
}
HTML_FORM = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Redeem Access Code</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    * {
      box-sizing: border-box;
    }
  
    body {
      margin: 0;
      padding: 0;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background: #f1f4f8;
      color: #333;
    }

    .container {
      max-width: 500px;
      background: white;
      padding: 30px;
      margin: 40px auto;
      border-radius: 12px;
      box-shadow: 0 0 20px rgba(0, 0, 0, 0.08);
    }

    h2 {
      text-align: center;
      color: #2e8b57;
      margin-bottom: 25px;
    }

    label {
      font-weight: bold;
      margin-bottom: 8px;
      display: block;
    }

    input[type="email"] {
      width: 100%;
      padding: 12px;
      margin-bottom: 20px;
      border-radius: 6px;
      border: 1px solid #ccc;
      font-size: 16px;
    }

    input[type="submit"] {
      background-color: #2e8b57;
      color: white;
      padding: 12px;
      width: 100%;
      font-size: 16px;
      border: none;
      border-radius: 6px;
      cursor: pointer;
      transition: background 0.3s ease;
    }

    input[type="submit"]:hover {
      background-color: #24744b;
    }

    .code-display {
      font-size: 36px;
      color: #28a745;
      text-align: center;
      margin-top: 20px;
    }

    .error {
      color: red;
      text-align: center;
      margin-top: 20px;
    }

    .instructions {
      margin-top: 40px;
      padding: 20px;
      background: #fff;
      border-radius: 10px;
      box-shadow: 0 0 10px rgba(0, 0, 0, 0.05);
    }

    .instructions h3 {
      color: #2e8b57;
    }

    .instructions ol {
      padding-left: 20px;
    }

    .instructions img {
      max-width: 100%;
      height: auto;
      margin-top: 10px;
      border-radius: 10px;
    }

    #loading {
      display: none;
      text-align: center;
      margin-top: 20px;
    }

    #loading img {
      width: 40px;
    }

    .mode-tabs{

    display:flex;
    gap:8px;
    margin-bottom:20px;

}

.mode-tabs button{

    flex:1;
    padding:10px;
    cursor:pointer;
    border-radius:6px;
    border:1px solid #ccc;
    background:#eee;
    font-weight:bold;

}

.mode-tabs button.active{

    background:#2e8b57;
    color:white;

}

.popup-bg{
    position:fixed;
    inset:0;
    background:rgba(0,0,0,.75);
    backdrop-filter:blur(10px);
    display:none;
    justify-content:center;
    align-items:center;
    z-index:9999;
}

.popup{
    background:#1b1b1f;
    width:90%;
    max-width:320px;
    padding:18px;
    border-radius:18px;
}

.popup img{
    width:100%;
    border-radius:14px;
    margin-bottom:20px;
}

.popup h2{
    color:white;
    font-size:20px;
    margin-bottom:10px;
}

.popup-desc{
    color:#9ca3af;
    line-height:1.6;
    font-size:14px;
}

.benefits{
    color:#d1d5db;
    line-height:1.7;
    margin:20px 0;
}

.join-btn{
    display:block;
    width:100%;
    padding:12px;
    background:#229ED9;
    color:white;
    text-align:center;
    text-decoration:none;
    border-radius:10px;
    font-weight:bold;
    margin-bottom:10px;
}

.cancel-btn{
    display:block;
    width:100%;
    padding:12px;
    background:#2b2b2b;
    color:white;
    text-align:center;
    text-decoration:none;
    border-radius:10px;
}

  </style>
</head>
<body>

  <div class="container">
    <h2>Redeem Access Code</h2>
    <form method="POST" id="redeem-form">


<input
    type="hidden"
    name="mode"
    id="mode"
    value="{{ mode }}"
>

<div class="mode-tabs">

<button
    id="household-btn"
    type="button"
    onclick="switchMode('/')">
🏠 Household
</button>

<button
    id="signin-btn"
    type="button"
    onclick="switchMode('/signin')">
🔑 Sign-In Code
</button>

<button
    id="verification-btn"
    type="button"
    onclick="switchMode('/verify')">
🛡 Verification
</button>

</div>


      
      <label for="email">Your @mantapnet.com Email:</label>
<input
    id="email"
    type="email"
    name="email"
    value="{{ prefill_email }}"
    placeholder="example@mantapnet.com"
    required>

      <input type="submit" value="Get Code">

      <div id="loading">
        <img src="/loading.gif" alt="Loading...">
        <p>Checking for your code...</p>
      </div>
    </form>

    {% if email %}
      <p style="text-align:center;">Email entered: <strong>{{ email }}</strong></p>
    {% endif %}
    {% if code %}
      <div class="code-display">{{ code }}</div>
    {% elif error %}
      <div class="error">{{ error }}</div>
    {% endif %}
  </div>

<div
    id="household-instruction"
    class="instructions container"
>

<h3>Household Instructions</h3>

<ol>
    <li>On TV tap <b>I'm Travelling</b>/On phone <b>Watch tempoorarily</b>.</li>
    <li>Tap <b>Send Email</b>.</li>
    <li>Enter your <b>@mantapnet.com</b> email.</li>
    <li>Click <b>Get Code</b>.</li>
</ol>

<div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:20px;">
    <img src="/tv.png">
    <img src="/fon.png">
</div>

</div>

<div
    id="signin-instruction"
    class="instructions container"
    style="display:none;"
>

<h3>Sign In Instructions</h3>

<ol>
    <li> <b>LETAK EMAIL </b>.</li>
    <li> <b>AMBIL CODE KAT KOTAK ATAS</b> </li>
    <li> <b>LETAK CODE DALAM KOTAK NETFLIX</b></li>
</ol>

<div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:20px;">
    <img src="/static/signin-1.png">
    <img src="/static/signin-3.png">
    <img src="/static/signin-2.png">

</div>


</div>

<div
    id="verification-instruction"
    class="instructions container"
    style="display:none;"
>

<h3>Verification Instructions</h3>

<ol>
    <li> <b>SIGN IN GUNA PASSWORD </b>.</li>
    <li> <b>TEKAN EMAIL A CODE /PENGANALAN KOD </b></li>
    <li> <b>LETAK EMAIL DALAM KOTAK ATAS</b></li>
    <li> <b>AMBIL CODE LETAK DLM KOTAK NETFLIX </b></li>
</ol>

<div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:20px;">
    <img src="/static/verify-1.png">
    <img src="/static/verify-2.png">
    <img src="/static/verify-3.png">
    <img src="/static/verify-4.png">
</div>

</div>

  <script>
function closePopup(){
    document.getElementById("popup").style.display="none";
}

window.onload = function () {

    setMode(
        document.getElementById("mode").value
    );

    if (!sessionStorage.getItem("promoShown")) {

        document.getElementById("popup").style.display = "flex";

        sessionStorage.setItem("promoShown", "true");
    }

}

function switchMode(path) {
    const email = document.getElementById("email").value.trim();

    if (email) {
        window.location = `${path}?email=${encodeURIComponent(email)}`;
    } else {
        window.location = path;
    }
}

 function setMode(mode){

    document.getElementById("mode").value = mode;

    document
        .querySelectorAll(".mode-tabs button")
        .forEach(btn=>btn.classList.remove("active"));

    document
        .getElementById(mode+"-btn")
        .classList.add("active");

    document.getElementById("household-instruction").style.display="none";
    document.getElementById("signin-instruction").style.display="none";
    document.getElementById("verification-instruction").style.display="none";

    document.getElementById(mode+"-instruction").style.display="block";
}



    document.getElementById("redeem-form").addEventListener("submit", function () {
      document.getElementById("loading").style.display = "block";
    });

    
  </script>
<div id="popup" class="popup-bg" onclick="closePopup()">

    <div class="popup" onclick="event.stopPropagation()">

        <img src="/static/sinchan_poster3.png">

        <h2>SINCHAN PREMIUM SHOP</h2>

        <p class="popup-desc">
            NETFLIX PREMIUM 4K Ultra HD Quality.
        </p>

        <div class="benefits">
            ✓ PREMIUM STABLE ACCOUNT<br>
            ✓ PRIVATE SLOT<br>
            ✓ 1 USER / 1 PROFILE<br>
            ✓ NO SCREEN LIMIT
        </div>

        <a
            class="join-btn"
            target="_blank"
            href="https://t.me/sinchan_shop">

            Join Telegram

        </a>

        <a
            href="#"
            class="cancel-btn"
            onclick="closePopup();return false;">

            Cancel

        </a>

    </div>

</div>
</body>
</html>

"""

@app.route("/fon.png")
def fon_link():
  external_url = "https://github.com/moviemembership/redeem-app/blob/485881a153a2ebc785e524b94f5a7d9fe232b157/fon.png?raw=true"
  return redirect(external_url)

@app.route("/tv.png")
def tv_link():
  external_url = "https://github.com/moviemembership/redeem-app/blob/main/tv.png?raw=true"
  return redirect(external_url)

@app.route("/loading.gif")
def loading_link():
  external_url = "https://github.com/moviemembership/redeem-app/blob/main/Loading_icon.gif?raw=true"
  return redirect(external_url)

@app.route("/", methods=["GET", "POST"])
@app.route("/signin", methods=["GET", "POST"])
@app.route("/verify", methods=["GET", "POST"])
def redeem():

    code = None
    error = None

    if request.path == "/signin":
        default_mode = "signin"
    elif request.path == "/verify":
        default_mode = "verification"
    else:
        default_mode = "household"

    mode = default_mode
    prefill_email = request.args.get("email", "")

    if request.method == "POST":
        user_email = request.form["email"].strip().lower()
        mode = request.form.get("mode", default_mode)

        try:
            mail = imaplib.IMAP4_SSL(IMAP_HOST)
            mail.login(ADMIN_EMAIL, ADMIN_PASS)
            mail.select("inbox")

            yesterday = (datetime.now() - timedelta(days=1)).strftime("%d-%b-%Y")

            subjects = SUBJECTS.get(mode)

            if not subjects:
                error = "Invalid mode."

            else:
                message_ids = search_emails(mail, subjects)

                if not message_ids:
                  error = f"No recent {mode} emails found."

                else:

                  msg, body = find_email(
                      mail,
                      message_ids,
                      user_email
                  )

                if not msg:
                    error = "No matching email found for that address."

                else:

                    if mode == "household":
                        code, error = parse_household(body)

                    elif mode == "signin":
                        code, error = parse_signin(body)

                    elif mode == "verification":
                        code, error = parse_verification(body)

            mail.logout()

        

        except Exception as e:
            traceback.print_exc()      # 印到 CMD
            error = traceback.format_exc()

    return render_template_string(
        HTML_FORM,
        code=code,
        error=error,
        email=user_email if request.method == "POST" else "",
        mode=mode,
        prefill_email=prefill_email
    )

def parse_verification(body):

    match = re.search(r"\b(\d{6})\b", body)

    if match:
        return match.group(1), None

    return None, "Unable to find verification code."

def parse_signin(body):

    match = re.search(r"\b(\d{4})\b", body)

    if match:
        return match.group(1), None

    return None, "Unable to find sign in code."

def parse_household(body):

    match = re.search(r'https?://[^\s"<>\]]+', body)

    link = match.group(0) if match else None

    if not link:
        return None, "No link found in the email."

    return extract_code_from_verification_link(link)

def find_email(mail, message_ids, user_email):

    user_email = user_email.lower()

    for msg_id in reversed(message_ids):

        status, msg_data = mail.fetch(msg_id, "(RFC822)")
        raw_email = msg_data[0][1]

        msg = email.message_from_bytes(raw_email)

        body = extract_email_body(msg)

        to_email = (msg.get("To") or "").lower()

        print("TO:", to_email)
        print("BODY:")
        print(body)
        print("=" * 50)

        if user_email in to_email or user_email in body.lower():
            return msg, body

    return None, None

def search_emails(mail, subjects):

    yesterday = (
        datetime.now() - timedelta(days=1)
    ).strftime("%d-%b-%Y")

    message_ids = []

    for subject in subjects:
        status, messages = mail.search(
            None,
            f'(SINCE {yesterday} SUBJECT "{subject}")'
        )

        if status == "OK":
            message_ids.extend(messages[0].split())

    return message_ids

def extract_email_body(msg):
    try:
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type in ["text/plain", "text/html"]:
                    payload = part.get_payload(decode=True)
                    return payload.decode(errors="ignore") if isinstance(payload, bytes) else str(payload)
        else:
            payload = msg.get_payload(decode=True)
            return payload.decode(errors="ignore") if isinstance(payload, bytes) else str(payload)
    except Exception:
        return ""

def extract_code_from_verification_link(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        if soup.find("div", class_="title", string="This link is no longer valid"):
            return None, "This code has expired. Please re-request on the original device. Please Make sure you have done the steps below and redeem it within 15 minutes."

        code_div = soup.find("div", {"data-uia": "travel-verification-otp"})
        if code_div:
            return code_div.text.strip(), None
        else:
            return None, "Unable to fetch code. Please Make Sure You Redeem It within 15 minutes. Contact customer support for more information."
    except Exception as e:
        print("Error while extracting code:", e)
        return None, "Unable to access the verification link. Try again later."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
