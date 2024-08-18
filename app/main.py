from fasthtml.common import *
from util import generate_responses
import sqlite3

title = "CIP Demo"
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

nav = Nav(
    A("Home", href="/"),
    A("New Policy Simulation", href="/simulate"),
    style="margin-bottom: 10px;"
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
    # TODO this is hacky. we do this because response format from generate_responses is different from querying sqlite
    # and I'm too lazy to find a better way to do this
    print("DEBUG", response)
    if len(response) == 2:
        demographics, text = response[0].values(), response[1]
    else:
        demographics, text = response[2:-1], response[-1]
    return Card(
        Div(*[Span(str(demographic), cls="kbd-style") for demographic in demographics], cls="card-header"),
        Div(text, cls="card-body", style="margin-top: 10px;"),
        cls="card"
    )

@router("/")
async def get():
    policies = cur.execute("SELECT * FROM policies").fetchall()
    policy_cards = [Card(
        Div(A("View Policy", href=f"/view?id={id}"), P(text), cls="card-body"), cls="card")
    for id, text in policies]
    
    return Title(title), Main(H1(title), nav, *policy_cards, cls='container')

@router("/simulate")
async def get():
    form = Form(
            Textarea(id="policy", name="policy", placeholder="Draft Policy", required=True),
            Button("Submit", type="submit"),
            hx_post="/simulate", target_id='response-list', hx_swap="beforeend")
    return Title(title), Main(H1(title), nav, form, Div(id="response-list"), cls='container')

@router("/simulate")
async def post(policy: str):
    print("Genearating responses...")
    cur.execute("INSERT INTO policies (text) VALUES (?)", (policy,))
    db.commit()
    policy_id = cur.lastrowid
    policy_responses = generate_responses(policy)
    for response in policy_responses:
        cur.execute("INSERT INTO responses (policy_id, political_leaning, age, ethnicity, gender, education_level, party, text) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (policy_id, *response[0].values(), response[1]))
        db.commit()
    return Div(*[response_card(response) for response in policy_responses])

@router("/view")
async def get(id: int):
    policy = cur.execute("SELECT * FROM policies WHERE id = ?", (id,)).fetchone()
    responses = cur.execute("SELECT * FROM responses WHERE policy_id = ?", (id,)).fetchall()
    policy_card = Card(
        Div(policy[1], cls="card-body"),
        cls="card"
    )
    response_cards = [response_card(response) for response in responses]
    return Title(title), Main(H1(title), nav, policy_card, *response_cards, cls='container')

serve()