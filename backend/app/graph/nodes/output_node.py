from app.model.state import InterviewState


def output_node(state: InterviewState) -> dict:
    print("inside output")
    return {
        "final_summary": state.final_summary
    }