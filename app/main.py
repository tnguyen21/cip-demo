from fasthtml.common import *
from util import generate_responses
import sqlite3

app, router = fast_app(
    hdrs=[Style("""
span.kbd-style {
    font-family: monospace;
    padding: 2px 4px;
    font-size: 90%;
    color: #333;
    background-color: #f7f7f7;
    border: 1px solid #ccc;
    border-radius: 3px;
    box-shadow: inset 0 -1px 0 #bbb;
}
""")]
)

# create data/demo.db if it doesn't exist
if not os.path.exists("demo.db"):
    with sqlite3.connect("demo.db") as db:
        cur = db.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS policies (id INTEGER PRIMARY KEY, text TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS responses (id INTEGER PRIMARY KEY, policy_id INTEGER, political_leaning TEXT, age INTEGER, ethnicity TEXT, gender TEXT, education_level TEXT, party TEXT, text TEXT)")
        db.commit()

db = sqlite3.connect("demo.db")
cur = db.cursor()

def response_card(response):
    demographic_info, text = response
    demographics = list(demographic_info.values())
    
    return Card(
        Div(*[Span(str(demographic), cls="kbd-style") for demographic in demographics], cls="card-header"),
        Div(text, cls="card-body", style="margin-top: 10px;"),
        cls="card"
    )

@router("/")
async def get():
    form = Form(
            Textarea(id="policy", name="policy", placeholder="Draft Policy", required=True),
            Button("Submit", type="submit"),
            hx_post="/", target_id='response-list', hx_swap="beforeend")

    title = "Demo"
    return Title(title), Main(H1(title), form, Div(id="response-list"), cls='container')

@router("/")
async def post(policy: str):
    print("Genearating responses...")
    print("DEBUG", policy)
    cur.execute("INSERT INTO policies (text) VALUES (?)", (policy,))
    db.commit()
    policy_id = cur.lastrowid
    policy_responses = generate_responses(policy)
    for response in policy_responses:
        cur.execute("INSERT INTO responses (policy_id, political_leaning, age, ethnicity, gender, education_level, party, text) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (policy_id, *response[0], response[1]))
        db.commit()
    return Div(*[response_card(response) for response in policy_responses])

serve()