from fsm_with_grid_eye import GridEye as ge

def test(event):
    print(event)

ge_object = ge(test)
ge_object.monitor()