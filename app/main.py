from fasthtml.common import *
from util import generate_responses

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


def response_card(response):
    demographic_info, text = response
    demographics = list(demographic_info.values())
    print(demographics)
    return Card(
        Div(*[Span(str(demographic), cls="kbd-style") for demographic in demographics], cls="card-header"),
        Div(text, cls="card-body", style="margin-top: 10px;"),
        cls="card"
    )

@router("/")
async def get():
    add = Form(
            Textarea(id="policy", name="policy", placeholder="Draft Policy", required=True),
            Button("Submit", type="submit"),
            hx_post="/", target_id='response-list', hx_swap="beforeend")

    card = Card(id="response-list",
            header=add, footer=Div()),
    
    title = "Demo"
    return Title(title), Main(H1(title), card, cls='container')

@router("/")
async def post(policy: str):
    print("Genearating responses...")
    responses = generate_responses(policy)
    return Div(*[response_card(response) for response in responses])

serve()