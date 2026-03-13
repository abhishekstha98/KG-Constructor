from kg_pipeline.services.uri_minter import URIMinter

def test_uri_minter_determinism():
    minter = URIMinter(base_uri="http://test.org/kg/")
    
    # Same input -> same ID
    id1 = minter.mint_document_id("file1.pdf")
    id2 = minter.mint_document_id("file1.pdf")
    assert id1 == id2
    
    # Different input -> diff ID
    id3 = minter.mint_document_id("file2.pdf")
    assert id1 != id3

    # Canonical URI minting
    uri1 = minter.mint_entity_uri("Barack Obama", "PERSON")
    assert uri1 == "http://test.org/kg/entity/person/barack_obama"

    # Event minting
    ev_uri = minter.mint_event_uri("acquired", "business_acquisition")
    assert ev_uri == "http://test.org/kg/event/business_acquisition/acquired"
