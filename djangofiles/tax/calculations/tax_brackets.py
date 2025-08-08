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
    }
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
    }
}