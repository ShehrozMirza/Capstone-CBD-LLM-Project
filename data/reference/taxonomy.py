"""
Normalized apparel taxonomy: category -> class -> trigger synonyms.

A class is assigned when one of its trigger phrases is found in the product's
title / description / categoryHierarchy. This is the cleaned, valid-Python
version of the provided taxonomy_dictionary.txt (the original had a few
unbalanced braces and a stray quote).

Extend or prune freely -- this is a starting point, not a mandate.
"""

CATS = {
    "accessories": {
        "bags": ['carryalls', 'holdalls', 'satchels', 'sacks', 'luggage', 'backpacks',
                 'suitcases', 'totes', 'purses', 'knapsacks', 'cases'],
        "belts": ['buckles', 'sash', 'sashes', 'bands'],
        "eyewear": ['glasses', 'spectacles', 'goggles', 'lenses', 'shades', 'contacts', 'readers'],
        "gloves": ['mittens'],
        "hats": ['caps', 'beanies', 'helmets', 'headgear', 'fedoras', 'sombreros', 'straws',
                 'headpieces', 'headbands', 'chapeaus', 'fezs', 'turbans'],
        "jewelry": ['golds', 'silvers', 'sterlings', 'watch', 'watches', 'earrings', 'brooch',
                    'brooches', 'tiaras', 'bracelets', 'necklaces', 'tie clips', 'chains',
                    'studs', 'cufflinks', 'rings', 'anklets', 'jewels'],
        "scarves": [],
        "ties": ['bows', 'knots', 'chokers', 'neckcloth'],
        "umbrellas": ['brellas', 'sunshade'],
        "wallets": ['pocketbooks'],
    },
    "assorted": {
        "beauty": ['makeup', 'eyeliner', 'lipstick'],
        "kids_juniors": [],
        "other": [],
    },
    "footwear": {
        "athletic": ['cleats', 'running shoes', 'track shoes', 'walking shoe', 'skate shoe',
                     'training shoe', 'golf shoe', 'tennis shoe', 'water shoe', 'cycling shoe',
                     'volleyball shoe', 'studio shoe', 'hiking shoe', 'dance shoe',
                     'basketball shoe', 'wrestling shoe', 'bowling shoe', 'cheerleading shoe',
                     'skateboarding', 'sport sandal', 'running shoe', 'crossfit shoe',
                     'sports shoe', 'track and field'],
        "boots": [' boot', 'booties', 'chelsea'],
        "clogs": ['clogs'],
        "drivers": ['drivers'],
        "loafers": ['loafers'],
        "mules": ['mules'],
        "oxfords": ['oxfords'],
        "pumps": ['pumps', 'heels'],
        "sandals": ['espadrilles', 'flat', 'flipflops', 'platform', 'sandal', 'wedge',
                    'flip flops', 'flip-flops'],
        "slippers": ['mocs', ' moc', 'slipon', 'moccasin', 'scuff', ' slides', 'slipper', 'thongragg'],
        "sneakers": ['sneakers'],
    },
    "fullbody": {
        "activewear": ['athletic wear', 'gym suit', 'sportswear', 'garb', 'running suit', 'sports apparel'],
        "dresses": ['frock', 'gown'],
        "jumpsuits": ['bodysuit', 'playsuit'],
        "overalls": ['boiler suit', 'coveralls', 'dungarees'],
        "robes": ['cloak', 'kaftan'],
        "rompers": ['bloomer'],
        "sleepwear": ['pjs', "pj's", 'nightgown', 'nightdress', 'bedgown', 'pajamas', 'negligee', 'nightshirt'],
        "suits": [],
    },
    "lingerie": {
        "bras": [' bra', 'brassiere', 'bralette', 'brasier', 'brasserie', ' cup'],
        "chemises": ['chemises'],
        "corsets_bustiers": ['corset', 'bustier'],
        "garters": [' garter'],
        "lingerie_accessories": ['nipple cover', 'nipplecover', 'breast cover', 'breastcover',
                                 'nipleless cover', 'body tape', 'bra extender', 'bra pad', 'coverups'],
        "panties": ['thong', 'bikinis', 'vstring', 'gstring', 'cheekie', 'cheekin', ' brazilian',
                    ' brief panty', 'hiphugger', 'shortie', 'pantie', 'bottom', 'hipster', 'boxer'],
        "shapewear": ['control pantie', 'thigh slimmer', 'waist cincher', 'bodysuit', ' control slip'],
        "slips": [' slip', ' tutu'],
        "tanks_camis": ['tank', 'cami', 'tanktop', 'camisole', 'camitop'],
    },
    "lowerbody": {
        "jeans": ['jean', 'denim'],
        "leggings": ['active pants', ' leggings', 'tights', 'yogapant', 'elasticpant', 'capri'],
        "underwear": ['bikini', 'boxer brief', 'boxer', 'brief', 'gstring', 'thong', 'shapewear',
                      'thermal underwear', 'trunk', 'undershirt', 'bottom'],
        "pants": ['scrub pants', 'track pants', 'knit pants', 'snow pants', 'dress pants', ' pants',
                  'sweatpants', 'khakis', 'chinos'],
        "shorts": ['cutoff pants', 'shorts'],
        "skirts": ['skirt'],
    },
    "outerwear": {
        "cardigans": ['pullover', 'shrug'],
        "coats_jackets": ['suit coat', 'suit jacket', 'coat', 'jacket', 'parka'],
        "suitcoats_blazers": ['blazer', 'sport coat'],
        "vests": ['burka', 'burqa', 'apron', 'vest'],
    },
    "swimwear": {
        "rash_guards": ['rash guard', 'rashguard'],
        "swimwear_tops": ['swim top'],
        "swimwear_bottoms": ['bathing trunks', 'bathing shorts', 'board shorts'],
        "swimwear_one_pieces": ['one piece bathing suit', 'swim bottom'],
        "swimwear_other": ['wetsuit'],
    },
    "upperbody": {
        "blouses": ['blouse'],
        "henleys": ['henley'],
        "hoodies": ['sweatshirt', 'hoodie'],
        "polos": ['collared shirt', 'polo'],
        "shirts": ['long sleeve shirt', 'long sleeve', 'long-sleeve', 'button-down', 'button down', 'shirt'],
        "sweaters": ['sweater'],
        "t_shirts": ['t shirt', 'tee shirt', 't-shirt', 'tshirt', 'teeshirt', 'tee-shirt'],
        "tunics": ['tunic'],
    },
}
