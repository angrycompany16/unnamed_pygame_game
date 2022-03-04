def square_rect(w, h):
    min_w = w
    min_h = h
    while min_w > 0:
        if min_w >= min_h:
            min_w -= min_h
        if min_w < min_h:
            min_h -= min_w
        if min_w == 0:
            print(f"for rektangel med sider {w}, {h} har det minste kvadratet du må bruke for å fylle det {min_h} som sidelengde")
        elif min_h == 0:
            print(f"for rektangel med sider {w}, {h} har det minste kvadratet du må bruke for å fylle det {min_w} som sidelengde")

square_rect(21, 28)