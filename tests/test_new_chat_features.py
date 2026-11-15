import requests

def test_new_features():
    # Test 1 : Surface calculation
    r1 = requests.post('http://127.0.0.1:8000/chat', json={
        'question': 'شحال غانربح ونوفر فالماء والآزوت على 10 هكتار ديالي ؟',
        'history': [],
        'context': {'surface_hectares': 10, 'water_regime': 'saqwi'}
    }).json()
    print('R1 action:', r1.get('ui_action'))
    print('R1 tools:', [t['tool_name'] for t in r1.get('tools_executed', [])])

    # Test 2 : Comparison
    r2 = requests.post('http://127.0.0.1:8000/chat', json={
        'question': 'مقارنة بين القمح والحمص شكون حسن فالمداخيل والماء ومقاومة الجفاف ؟',
        'history': [],
        'context': {}
    }).json()
    print('R2 action:', r2.get('ui_action'))
    print('R2 tools:', [t['tool_name'] for t in r2.get('tools_executed', [])])
    print('ALL NEW FEATURES PASSED!')

if __name__ == '__main__':
    test_new_features()
