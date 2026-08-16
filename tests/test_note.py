from sticky_notes.note import Note

def test_note_has_required_fields():
    note = Note(id="1", text="hello", color="yellow")
    assert note.id == "1"
    assert note.text == "hello"
    assert note.color == "yellow"
