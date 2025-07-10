import plotly.graph_objects as go


def main():
    data = [
        go.Bar(
            x=['Q1', 'Q2', 'Q3', 'Q4'],
            y=[150, 200, 250, 300],
            name='New York',
            offsetgroup="USA"
        ),
        go.Bar(
            x=['Q1', 'Q2', 'Q3', 'Q4'],
            y=[180, 220, 270, 320],
            name='Boston',
            offsetgroup="USA"
        ),
        go.Bar(
            x=['Q1', 'Q2', 'Q3', 'Q4'],
            y=[130, 170, 210, 260],
            name='Montreal',
            offsetgroup="Canada"
        ),
        go.Bar(
            x=['Q1', 'Q2', 'Q3', 'Q4'],
            y=[160, 210, 260, 310],
            name='Toronto',
            offsetgroup="Canada"
        )
    ]

    layout = go.Layout(
        title={
            'text': 'Quarterly Sales by City, Grouped by Country'
        },
        xaxis={
            'title': {
                'text': 'Quarter'
            }
        },
        yaxis={
            'title': {
                'text': 'Sales'
            }
        },
        barmode='stack'
    )

    fig = go.Figure(data=data, layout=layout)

    # Write to an HTML file so it can be opened in any browser without running a server.
    output_file = "quarterly_sales_plot.html"
    fig.write_html(output_file, include_plotlyjs='cdn')
    print(f"Plot written to {output_file}. Open it in your browser to view the chart.")


if __name__ == "__main__":
    main() 