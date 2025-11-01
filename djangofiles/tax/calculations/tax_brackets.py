from decimal import Decimal


ORDINARY_TAX_TABLES = {
    "2024": {
        "single": {
            ".10": [Decimal("0"), Decimal("11600"), Decimal("0")],
            ".12": [Decimal("11601"), Decimal("47150"), Decimal("1160")],
            ".22": [Decimal("47151"), Decimal("100525"), Decimal("5426")],
            ".24": [Decimal("100526"), Decimal("191950"), Decimal("17169")],
            ".32": [Decimal("191951"), Decimal("243725"), Decimal("39111")],
            ".35": [Decimal("243726"), Decimal("609350"), Decimal("55679")],
            ".37": [Decimal("609351"), Decimal("1000000000"), Decimal("183647")]
        },
        "MFJ": {
            ".10": [Decimal("0"), Decimal("23200"), Decimal("0")],
            ".12": [Decimal("23201"), Decimal("94300"), Decimal("2320")],
            ".22": [Decimal("94301"), Decimal("201050"), Decimal("10852")],
            ".24": [Decimal("201051"), Decimal("383900"), Decimal("34337")],
            ".32": [Decimal("383901"), Decimal("487450"), Decimal("78221")],
            ".35": [Decimal("487451"), Decimal("731200"), Decimal("111357")],
            ".37": [Decimal("731201"), Decimal("1000000000"), Decimal("196670")]
        }
    },
    "2023": {
        "single": {
            ".10": [Decimal("0"), Decimal("11000"), Decimal("0")],
            ".12": [Decimal("11001"), Decimal("44725"), Decimal("1100")],
            ".22": [Decimal("44726"), Decimal("95375"), Decimal("5147")],
            ".24": [Decimal("95376"), Decimal("182100"), Decimal("16290")],
            ".32": [Decimal("182101"), Decimal("231250"), Decimal("37104")],
            ".35": [Decimal("231251"), Decimal("578125"), Decimal("52832")],
            ".37": [Decimal("578126"), Decimal("1000000000"), Decimal("174238")]
        },
        "MFJ": {
            ".10": [Decimal("0"), Decimal("22000"), Decimal("0")],
            ".12": [Decimal("22001"), Decimal("89450"), Decimal("2200")],
            ".22": [Decimal("89451"), Decimal("190750"), Decimal("10294")],
            ".24": [Decimal("190751"), Decimal("364200"), Decimal("32580")],
            ".32": [Decimal("364201"), Decimal("462500"), Decimal("74208")],
            ".35": [Decimal("462501"), Decimal("693750"), Decimal("105664")],
            ".37": [Decimal("693751"), Decimal("1000000000"), Decimal("186601.5")]
        }
    },
    "2022": {
        "single": {
            ".10": [Decimal("0"), Decimal("10275"), Decimal("0")],
            ".12": [Decimal("10276"), Decimal("41775"), Decimal("1027.5")],
            ".22": [Decimal("41776"), Decimal("89075"), Decimal("4807.5")],
            ".24": [Decimal("89076"), Decimal("170050"), Decimal("15213.5")],
            ".32": [Decimal("170051"), Decimal("215950"), Decimal("34647.5")],
            ".35": [Decimal("215951"), Decimal("539900"), Decimal("49335.5")],
            ".37": [Decimal("539901"), Decimal("1000000000"), Decimal("162718")]
        },
        "MFJ": {
            ".10": [Decimal("0"), Decimal("20550"), Decimal("0")],
            ".12": [Decimal("20551"), Decimal("83550"), Decimal("2055")],
            ".22": [Decimal("83551"), Decimal("178150"), Decimal("9615")],
            ".24": [Decimal("178151"), Decimal("340100"), Decimal("30427")],
            ".32": [Decimal("340101"), Decimal("431900"), Decimal("69294")],
            ".35": [Decimal("431901"), Decimal("647850"), Decimal("98670")],
            ".37": [Decimal("647851"), Decimal("1000000000"), Decimal("174252")]
        }
    },
    "2021": {
        "single": {
            ".10": [Decimal("0"), Decimal("9950"), Decimal("0")],
            ".12": [Decimal("9951"), Decimal("40525"), Decimal("995")],
            ".22": [Decimal("40526"), Decimal("86375"), Decimal("4664")],
            ".24": [Decimal("86376"), Decimal("164925"), Decimal("14751")],
            ".32": [Decimal("164926"), Decimal("209425"), Decimal("33603")],
            ".35": [Decimal("209426"), Decimal("523600"), Decimal("47843")],
            ".37": [Decimal("523601"), Decimal("1000000000"), Decimal("157804.25")]
        },
        "MFJ": {
            ".10": [Decimal("0"), Decimal("19900"), Decimal("0")],
            ".12": [Decimal("19901"), Decimal("81050"), Decimal("1990")],
            ".22": [Decimal("81051"), Decimal("172750"), Decimal("9328")],
            ".24": [Decimal("172751"), Decimal("329850"), Decimal("29502")],
            ".32": [Decimal("329851"), Decimal("418850"), Decimal("67206")],
            ".35": [Decimal("418851"), Decimal("628300"), Decimal("95686")],
            ".37": [Decimal("628301"), Decimal("1000000000"), Decimal("168993.5")]
        }
    },
    "2020": {
        "single": {
            ".10": [Decimal("0"),         Decimal("9875"),   Decimal("0")],
            ".12": [Decimal("9876"),     Decimal("40125"),  Decimal("987.5")],
            ".22": [Decimal("40126"),    Decimal("85525"),  Decimal("4617.5")],
            ".24": [Decimal("85526"),    Decimal("163300"), Decimal("14605.5")],
            ".32": [Decimal("163301"),   Decimal("207350"), Decimal("33271.5")],
            ".35": [Decimal("207351"),   Decimal("518400"), Decimal("47367.5")],
            ".37": [Decimal("518401"),   Decimal("1000000000"), Decimal("156235")]
        },
        "MFJ": {
            ".10": [Decimal("0"),         Decimal("19750"),  Decimal("0")],
            ".12": [Decimal("19751"),    Decimal("80250"),  Decimal("1975.0")],
            ".22": [Decimal("80251"),    Decimal("171050"), Decimal("9235.0")],
            ".24": [Decimal("171051"),   Decimal("326600"), Decimal("29211.0")],
            ".32": [Decimal("326601"),   Decimal("414700"), Decimal("66543.0")],
            ".35": [Decimal("414701"),   Decimal("622050"), Decimal("9435.0")],
            ".37": [Decimal("62251"),   Decimal("1000000000"), Decimal("167307.5")]
        }
    },
    "2019": {
        "single": {
            ".10": [Decimal("0"),         Decimal("9700"),   Decimal("0")],
            ".12": [Decimal("9701"),     Decimal("39475"),  Decimal("970.0")],
            ".22": [Decimal("39476"),    Decimal("84200"),  Decimal("4543.5")],
            ".24": [Decimal("84201"),    Decimal("160725"), Decimal("14382.5")],
            ".32": [Decimal("160726"),   Decimal("204100"), Decimal("32748.5")],
            ".35": [Decimal("204101"),   Decimal("510300"), Decimal("46628.5")],
            ".37": [Decimal("510301"),   Decimal("1000000000"), Decimal("153798.5")]
        },
        "MFJ": {
            ".10": [Decimal("0"),         Decimal("19400"),  Decimal("0")],
            ".12": [Decimal("19401"),    Decimal("78950"),  Decimal("1940.00")],
            ".22": [Decimal("78951"),    Decimal("168400"), Decimal("9086.00")],
            ".24": [Decimal("168401"),   Decimal("321450"), Decimal("28765.00")],
            ".32": [Decimal("321451"),   Decimal("408200"), Decimal("65497.00")],
            ".35": [Decimal("408201"),   Decimal("612350"), Decimal("93257")],
            ".37": [Decimal("612351"),   Decimal("1000000000"), Decimal("164709.5")]
        }
    },
    "2018": {
        "single": {
            ".10": [Decimal("0"),         Decimal("9525"),   Decimal("0")],
            ".12": [Decimal("9526"),     Decimal("38700"),  Decimal("952.5")],
            ".22": [Decimal("38701"),    Decimal("82500"),  Decimal("4453.5")],
            ".24": [Decimal("82501"),    Decimal("157500"), Decimal("14089.5")],
            ".32": [Decimal("157501"),   Decimal("200000"), Decimal("32089.5")],
            ".35": [Decimal("200001"),   Decimal("500000"), Decimal("45689.5")],
            ".37": [Decimal("500001"),   Decimal("1000000000"), Decimal("150689.5")]
        },
        "MFJ": {
            ".10": [Decimal("0"),         Decimal("19050"),  Decimal("0")],
            ".12": [Decimal("19051"),    Decimal("77400"),  Decimal("1905.0")],
            ".22": [Decimal("77401"),    Decimal("165000"), Decimal("8907.0")],
            ".24": [Decimal("165001"),   Decimal("315000"), Decimal("28179.0")],
            ".32": [Decimal("315001"),   Decimal("400000"), Decimal("64179.0")],
            ".35": [Decimal("400001"),   Decimal("600000"), Decimal("91379.0")],
            ".37": [Decimal("600001"),   Decimal("1000000000"), Decimal("161379.0")]
        }
    },
}

QUALIFIED_TAX_TABLES = {
    "2024": {
        "single": {
            "0": [Decimal("0"), Decimal("47025")],
            ".15": [Decimal("47026"), Decimal("518900")],
            ".20": [Decimal("518901"), Decimal("10000000")]
        },
        "MFJ": {
            "0": [Decimal("0"), Decimal("94050")],
            ".15": [Decimal("94051"), Decimal("583750")],
            ".20": [Decimal("583751"), Decimal("10000000")]
        }
    },
    "2023": {
        "single": {
            "0": [Decimal("0"), Decimal("44625")],
            ".15": [Decimal("44626"), Decimal("492300")],
            ".20": [Decimal("492301"), Decimal("10000000")]
        },
        "MFJ": {
            "0": [Decimal("0"), Decimal("89250")],
            ".15": [Decimal("89251"), Decimal("553850")],
            ".20": [Decimal("553851"), Decimal("10000000")]
        }
    },
    "2022": {
        "single": {
            "0": [Decimal("0"), Decimal("41675")],
            ".15": [Decimal("41676"), Decimal("459750")],
            ".20": [Decimal("459751"), Decimal("10000000")]
        },
        "MFJ": {
            "0": [Decimal("0"), Decimal("83350")],
            ".15": [Decimal("83351"), Decimal("517200")],
            ".20": [Decimal("517201"), Decimal("10000000")]
        }
    },
    "2021": {
        "single": {
            "0": [Decimal("0"), Decimal("40400")],
            ".15": [Decimal("40401"), Decimal("445850")],
            ".20": [Decimal("445851"), Decimal("10000000")]
        },
        "MFJ": {
            "0": [Decimal("0"), Decimal("80800")],
            ".15": [Decimal("80801"), Decimal("501600")],
            ".20": [Decimal("501601"), Decimal("10000000")]
        }
    },
    "2020": {
        "single": {
            "0": [Decimal("0"),         Decimal("40000")],
            ".15": [Decimal("40001"),   Decimal("441450")],
            ".20": [Decimal("441451"),   Decimal("1000000000")]
        },
        "MFJ": {
            "0": [Decimal("0"),         Decimal("80000")],
            ".15": [Decimal("80001"),   Decimal("496600")],
            ".20": [Decimal("496601"),   Decimal("1000000000")]
        }
    },
    "2019": {
        "single": {
            "0": [Decimal("0"),         Decimal("39375")],
            ".15": [Decimal("39376"),   Decimal("434550")],
            ".20": [Decimal("434551"),   Decimal("1000000000")]
        },
        "MFJ": {
            "0": [Decimal("0"),         Decimal("78750")],
            ".15": [Decimal("78751"),   Decimal("488850")],
            ".20": [Decimal("488851"),   Decimal("1000000000")]
        }
    },
    "2018": {
        "single": {
            "0": [Decimal("0"),         Decimal("38600")],
            ".15": [Decimal("38601"),   Decimal("425800")],
            ".20": [Decimal("425801"),  Decimal("1000000000")]
        },
        "MFJ": {
            "0": [Decimal("0"),         Decimal("77200")],
            ".15": [Decimal("77201"),   Decimal("479000")],
            ".20": [Decimal("479001"),  Decimal("1000000000")]
        }
    },
}