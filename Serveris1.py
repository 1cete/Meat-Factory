import socket
import random
import os
import time
import math
import sys, select
import threading

SOKETO_FAILAS = "./zaidimas.sock"
ZAIDIMO_STATISTIKA = "./taskai.dat"



###############################################################################
def rasykStatistika(klientas):
    failas = open(ZAIDIMO_STATISTIKA, 'a')
    failas.write(f'{klientas}\n')
    failas.close()
    
def dataLaikas(dt):
    rez = f'{dt.year}-{dt.month}-{dt.day}, {dt.hour}:{dt.minute}:{dt.second}'
    return rez
  
###############################################################################


class Klientas:
    def __init__(self, vardas):
        self.vardas = vardas
        self.pinigai = 50
        self.mesa = 50  
        self.pakuotes = 5  
        self.uzsakymai = []  
        self.masina_sugedo = False
        self.reali_praejo_laikas = 0 
        
        # The 4 types of sausages we have in *inventory* (starting 0).
        self.virtos = 0
        self.vytintos = 0
        self.karstos = 0
        self.saltos = 0
        
        
    def __str__(self):
        return (
            f"{self.vardas};"
            f"{self.pinigai};"
            f"{self.mesa};"
            f"{self.pakuotes};"
            f"{self.uzsakymai};"
            f"{self.masina_sugedo};"
            f"{self.reali_praejo_laikas}"
        )

class Uzsakymas:
    def __init__(self, virtos=0, vytintos=0, karstos=0, saltos=0, laiko_trukme=1):
               
        # Kiekvienos dešros kiekis
        self.virtos = virtos
        self.vytintos = vytintos
        self.karstos = karstos
        self.saltos = saltos
        
        self.laiko_trukme = laiko_trukme  # Paros skaičius
        self.laiko_pradzia = 0  
        self.delspinigiai = 0  
        self.laiko_pabaiga = 0  
        self.ivykdytas = False
        
        # Pelnas: 2 eurai už kiekvieną dešrą
        total_count = virtos + vytintos + karstos + saltos
        self.pelnas = total_count * 2

    def nustatyti_laiko_pabaiga(self, laiko_pradzia):
        # 1 para = 30 s realaus laiko
        self.laiko_pabaiga = laiko_pradzia + (self.laiko_trukme * 30)

    def pridet_delspinigiai(self, realus_praeje_laikas):
        if self.ivykdytas:
            return
        if realus_praeje_laikas >= self.laiko_pabaiga:
            velavimas = realus_praeje_laikas - self.laiko_pabaiga
            if velavimas > 0:
                # Kiek 5 sekundžių prabėgo nuo laiko pabaigos
                intervalai = int(velavimas // 5)
                # Nustatome delspinigius = intervalai * 1 €
                self.delspinigiai = intervalai * 1

    def __str__(self):
        return (
            f"(virtos={self.virtos}, vytintos={self.vytintos}, karštos={self.karstos}, "
            f"šaltos={self.saltos}, delspinigiai={self.delspinigiai}, ivykdytas={self.ivykdytas})"
        )

###############################################################################

def parodyti_uzsakymus(zaidejas):
    """Išveda visus užsakymus (kiek kokios dešros, kiek liko dienų, delspinigiai)."""
    if not zaidejas.uzsakymai:
        return "Šiuo metu nėra užsakymų.\n"
    lines = []
    for i, u in enumerate(zaidejas.uzsakymai, start=1):
        likusios_sekundes = max(u.laiko_pabaiga - zaidejas.reali_praejo_laikas, 0)
        likusios_dienos = likusios_sekundes // 30
        lines.append(
            f"{i}) virtos: {u.virtos}, vytintos: {u.vytintos}, "
            f"karštos: {u.karstos}, šaltos: {u.saltos}, "
            f"Liko: {likusios_dienos} d., delspinigiai: {u.delspinigiai} €"
            f"\nUž šį užsakymą gausite: {u.pelnas} €\n"
        )
    return "\n".join(lines) + "\n"

###############################################################################

def naujas_uzsakymas(zaidejas):
    # vietoj random(5..30) mėsos => random(0..10) virtų, etc.
    virtos = random.randint(0, 10)
    vytintos = random.randint(0, 10)
    karstos = random.randint(0, 10)
    saltos = random.randint(0, 10)
    laiko_trukme = random.choice([1,2,3,4])

    u = Uzsakymas(virtos, vytintos, karstos, saltos, laiko_trukme)
    u.laiko_pradzia = zaidejas.reali_praejo_laikas
    u.nustatyti_laiko_pabaiga(zaidejas.reali_praejo_laikas)

    zaidejas.uzsakymai.append(u)

    return (
        f"\nNaujas užsakymas: virtos: {virtos}, vytintos: {vytintos}, karštos: {karstos}, šaltos: {saltos}\n"
        f"Trukmė: {laiko_trukme} paros\n"
        f"Už šį užsakymą gausite: {u.pelnas} €\n"
    )


################################################################################

def uzsakymu_sarasas_tekstu(zaidejas):
    """Naudojame tą pačią logiką kaip parodyti_uzsakymus."""
    return parodyti_uzsakymus(zaidejas)

###############################################################################


def pirkti_resursus(zaidejas, pasirinkimas):
    """
    Grąžina eilutę, kurią vėliau serveris nusiųs klientui.
    Parametras 'pasirinkimas' turėtų būti '1' arba '2'.
    """
    atsakymas = ""
    atsakymas += "Parduotuvių pasirinkimai:\n"
    atsakymas += "1. Ūkininkas Antanas - Mėsos 10 kg už 10€\n"
    atsakymas += "2. Pakuočių parduotuvė - 5 pakuotės už 5€\n"

    if pasirinkimas == "1":
        atsakymas += "                                                         .'T'. - -'.\n"
        atsakymas += "                                                      .'/|||||\\'. - -'.\n"
        atsakymas += "                                                    .'/|||||||||\\'. - -'.\n"
        atsakymas += "                                                  .'/|||||___|||||\\'. - -'.\n"
        atsakymas += "    Jūs pasirinkote ūkininką Antaną!             //|||||||||||||||||\\\\ - - \\\n"
        atsakymas += "                                                //|||||||||||||||||||\\\\ - - \\  /|\\   Perduok linkėjimus šeimai!!\n"
        atsakymas += "                                               //|||||||||||||||||||||\\\\_____/\\//|\\\\               .\n"
        atsakymas += "                                                |||||||||||||||||||||| |||||  //|\\\\                .\n"
        atsakymas += "                         ____________::___      ||||||||||ldb||||||||| ||||| ///|\\\\\\             _/V\\_ \n"
        atsakymas += "          _        _    /_)_)_)_)_)_)_)_)/\\     ||||| \\       // |||| ||||| ///|\\\\\\              (d_b) ,\n"
        atsakymas += "         ( )_    _( )  /_)_)_)_)_)_)_)_)/ _\\    |||||   \\   //   |||| |||||////|\\\\\\\\           .__/Y\\_/\n"
        atsakymas += "        (  )_)  (  )_)  | :__:    :__: |: |     |||||     \\x\\     |||| |||||////|\\\\\\\\             |I|\n"
        atsakymas += "       (_(_ (_)(_) _)_) |  _   .-.   _ | :|     |||||   //   \\\\   |||| ||||/////|\\\\\\\\\\            / |\n"
        atsakymas += "     ____)\_(____)_/(___|_'_'o8|'|8o'_'|:_o8o._.o8%8o_//_______\\\\_||||.o88o8&8o)/(88o.____       _| |_ \n"

        if zaidejas.pinigai >= 10:
            zaidejas.mesa += 10
            zaidejas.pinigai -= 10
            atsakymas += "\n"
            atsakymas += "Įsigijote 10 kg mėsos.\n"
        else:
            atsakymas += "Nepakanka pinigų!\n"

    elif pasirinkimas == "2":
        atsakymas += "                                         .---__----.\n" 
        atsakymas += "                                       ;-------------.| \n"
        atsakymas += "                                       |             ||    .--__---. \n"
        atsakymas += " Jūs pasirinkote pakuočių parduotuvę!  |             ||  ;-----------.|\n"
        atsakymas += "                                       |             ||  |           ||\n"
        atsakymas += "                                       |_____________|/  |           ||\n"
        atsakymas += "                                                         |___________|/\n"
        if zaidejas.pinigai >= 5:
            zaidejas.pakuotes += 5
            zaidejas.pinigai -= 5
            atsakymas += "Įsigijote 5 pakuotes.\n"
        else:
            atsakymas += "Nepakanka pinigų!\n"
    else:
        atsakymas += "Neteisingas pasirinkimas!\n"

    return atsakymas


###############################################################################
def vykdyti_uzsakyma(zaidejas, uzsakymas_index):
    """
    Norime patikrinti, ar žaidėjas turi pakankamai DEŠRŲ (virtos, vytintos, karštos, šaltos),
    kad įvykdytų užsakymą. Jei taip, jas atimame, pridedame pelną, šaliname užsakymą iš sąrašo.
    """
    ats = ""
    try:
        u = zaidejas.uzsakymai[uzsakymas_index]
        # Tikriname, ar žaidėjas turi pakankamai dešrų:
        if (zaidejas.virtos >= u.virtos and
            zaidejas.vytintos >= u.vytintos and
            zaidejas.karstos >= u.karstos and
            zaidejas.saltos >= u.saltos):
            
            zaidejas.virtos -= u.virtos
            zaidejas.vytintos -= u.vytintos
            zaidejas.karstos -= u.karstos
            zaidejas.saltos -= u.saltos

            zaidejas.pinigai += u.pelnas
            u.ivykdytas = True
            ats += (
                f"Užsakymas įvykdytas (virtos={u.virtos}, vytintos={u.vytintos}, "
                f"karštos={u.karstos}, šaltos={u.saltos}).\n"
                f"Gavote {u.pelnas} eur.\n"
                f"Dėkojame!\n"
            )
            del zaidejas.uzsakymai[uzsakymas_index]
        else:
            ats += "Nepakanka dešrų atsargų šiam užsakymui!\n"
    except IndexError:
        ats += "Tokio užsakymo nėra!\n"
    return ats

###############################################################################

# cia issaugoju nauja gamybos sistema, bet poto padaryk, jog atrodytu labiau kaip originali versija

def gaminti_desras(zaidejas, komanda):
    """
    Iš žaliavų (mėsos, pakuočių) gaminame 4 rūšių dešrų.
    Pvz. komanda '2 1 0 3' -> virtos=2, vytintos=1, karstos=0, saltos=3.
    """
    parts = komanda.split()
    if len(parts) != 4:
        return (
            "Neteisingas formatas! Pvz: '2 1 0 5', reiškia: \n"
            " virtos=2, vytintos=1, karštos=0, saltos=5\n"
        )
    try:
        virtos = int(parts[0])
        vytintos = int(parts[1])
        karstos = int(parts[2])
        saltos = int(parts[3])
    except ValueError:
        return "Neteisinga įvestis! Reikia keturių sveikų skaičių.\n"

    # Kiek mėsos/pakuočių reikia vienai dešrai:
    # virtos: 2 kg mėsos, 1 pakuotė
    # vytintos: 3 kg mėsos, 1 pakuotė
    # karštos: 4 kg mėsos, 2 pakuotės
    # šaltos: 5 kg mėsos, 2 pakuotės
    mesa_needed = (
        virtos * 2 +
        vytintos * 3 +
        karstos * 4 +
        saltos * 5
    )
    pak_needed = (
        virtos * 1 +
        vytintos * 1 +
        karstos * 2 +
        saltos * 2
    )

    msg = f"Gaminame dešras: virtos={virtos}, vytintos={vytintos}, karštos={karstos}, šaltos={saltos}\n"
    msg += f"Reikės {mesa_needed} kg mėsos, {pak_needed} pakuočių.\n"

    if zaidejas.mesa >= mesa_needed and zaidejas.pakuotes >= pak_needed:
        # Užtenka resursų, gaminame
        zaidejas.mesa -= mesa_needed
        zaidejas.pakuotes -= pak_needed

        zaidejas.virtos   += virtos
        zaidejas.vytintos += vytintos
        zaidejas.karstos  += karstos
        zaidejas.saltos   += saltos

        msg += "Gamyba pavyko! Dešrų inventorius atnaujintas.\n"
    else:
        msg += "Nepakanka žaliavų!\n"
    return msg


##############################################################################
# Pagrindinė (vienkartinė) informacija, kurią norime rodyti "non-stop"

def suformuok_meniu(zaidejas):
    pranesimas1 = (
        f"\n                 ---------------"
        f"\n                | UAB ŠLAPIANKA |\n"
        f"                 ---------------\n"
        f"\n "
        f"         ) ) )                     ) ) )\n"\
        f"        ( ( (                      ( ( (\n"\
        f"      ) ) )                       ) ) )\n"\
        f"   (~~~~~~~~~)                 (~~~~~~~~~)\n"\
        f"    | DEŠRA |                   | DEŠRA |\n"\
        f"    |       |                   |       |\n"\
        f"    I      _._                  I       _._\n"\
        f"    I    /'   `\\                I     /'   `\\\n"\
        f"    I   |   N   |               I    |   N   |\n"\
        f"    f   |   |~~~~~~~~~~~~~~|    f    |    |~~~~~~~~~~~~~~|\n"\
        f"  .'    |   ||~~~~~~~~|    |  .'     |    | |~~~~~~~~|   |\n"\
        f"/'______|___||__###___|____|/'_______|____|_|__###___|___|\n"
        f"\n"
        f"Žaidėjo vardas: {zaidejas.vardas}\n"
        f"\nBŪSENA:\nPinigai: {zaidejas.pinigai}€, "
        f"Mėsa: {zaidejas.mesa} kg, pakuotės: {zaidejas.pakuotes}.\n"
        f"DEŠRŲ INVENTORIUS:\n"
        f"virtos: {zaidejas.virtos}, vytintos: {zaidejas.vytintos}, karštos: {zaidejas.karstos}, šaltos: {zaidejas.saltos}\n"
    )
    uzsakymai_tekstas = "\nUŽSAKYMAI:\n" + uzsakymu_sarasas_tekstu(zaidejas)
    pranesimas2 = (
        f"\nPasirinkite veiksmą:\n"
        f"1. Gaminti mėsos produktą\n"
        f"2. Parduotuves\n"
        f"3. Naujas užsakymas\n"
        f"4. Vykdyti užsakymą\n"
        f"0. Baigti žaidimą\n"
    )

    # Surenkame viską į vieną "didžiulį" tekstą
    return pranesimas1 + uzsakymai_tekstas + pranesimas2

###############################################################################

def laiko_atnaujinimas(zaidejas, interval=1):
    while not zaidejas.masina_sugedo:
        time.sleep(interval)
        zaidejas.reali_praejo_laikas += interval
        if tikrink_delspinigius(zaidejas):
            # Siųsti žinutę klientui apie bankrotą
            # Reikia įgyvendinti signalizavimo mechanizmą
            zaidejas.masina_sugedo = True
            break

###############################################################################

def tikrink_delspinigius(zaidejas):
    """
    Praeina 'reali_praejo_laikas' sekundžių.
    Tiems užsakymams, kuriems 'reali_praejo_laikas >= laiko_pabaiga',
    kas 5 realias sekundes po 'laiko_pabaiga' pridedame delspinigių.
    Jei delspinigiai > zaidejas.pinigai -> bankrotas (gražiname True ar pan.).
    """
    total_delspinigiai = 0  # Pridedame bendrą delspinigių sumą
    for uzs in zaidejas.uzsakymai:
        if not uzs.ivykdytas:
            if zaidejas.reali_praejo_laikas >= uzs.laiko_pabaiga:
                uzs.pridet_delspinigiai(zaidejas.reali_praejo_laikas)
                total_delspinigiai += uzs.delspinigiai
                if uzs.delspinigiai > zaidejas.pinigai:
                    return True  # Bankrotas
    return False  # Dar nebankrutavo

###############################################################################

def nustatyti_laiko_pabaiga(self, laiko_pradzia):
    # laiko_trukme (pvz. 2) => 2 paros => realiai 2*30 = 60 sek
    self.laiko_pabaiga = laiko_pradzia + (self.laiko_trukme * 30)


###############################################################################

def valdykKlienta(klientoSoketas):
    try:
        # 1. Paklausiame vardo
        serverioPranesimas = "Sveiki... Koks Jūsų vardas?\n"
        klientoSoketas.sendall(serverioPranesimas.encode('utf-8'))

        atsakymas = klientoSoketas.recv(4096).decode('utf-8')
        if not atsakymas:
            raise Exception("Nepavyko gauti atsakymo. Klientas gal atsijungė?")

        vardas = atsakymas.strip()
        zaidejas = Klientas(vardas)

      
        last_tick = time.time()  # Fiksuojame laiką, kai pradedame

        # 3. Pirmą kartą atsiunčiame meniu
        visas_meniu = suformuok_meniu(zaidejas)
        klientoSoketas.sendall(visas_meniu.encode('utf-8'))
        
        # Pradėkite laiko atnaujinimo thread'ą
        laiko_thread = threading.Thread(target=laiko_atnaujinimas, args=(zaidejas,))
        laiko_thread.start()

        # 4. Pradedame ciklą laukti veiksmų
        while True:
            duomenys = klientoSoketas.recv(4096)
            if not duomenys:
                # gauta tuščia -> nutraukti
                break

           
            # Kviečiame tikrink_delspinigius
            if tikrink_delspinigius(zaidejas):
                klientoSoketas.sendall(b"Jus bankrutavote (delspinigiai virsijo turimus pinigus)!\n")
                break
                
            if zaidejas.masina_sugedo:
                klientoSoketas.sendall(b"Jus bankrutavote (delspinigiai virsijo turimus pinigus)!\n")
                break

            komanda = duomenys.decode('utf-8').strip()
            if not komanda:
                # Jeigu vartotojas tiesiog spaudžia Enter,
                # praleidžiame šį žingsnį (nenutraukiame žaidimo).
                klientoSoketas.sendall(b"Prasome ivesti komanda, o ne tuscia eilute.\n")
                continue

                """ Ir toliau rodom meniu
                visas_meniu = suformuok_meniu(zaidejas)
                klientoSoketas.sendall(visas_meniu.encode('utf-8'))
                continue"""

            #komanda = duomenys.decode('utf-8').strip()
            if komanda == "0":
                klientoSoketas.sendall(b"Baigiam zaidima...\n")
                break

            elif komanda == "1":
                # Gaminti 4 rūšių dešras iš mėsos/pakuočių
                paaiskinimas = (
                    "\nKiekvienai dešrai reikalingi žaliaviniai resursai:\n"
                    "  - virtos: 2 kg mėsos, 1 pakuotė.\n"
                    "  - vytintos: 3 kg mėsos, 1 pakuotė.\n"
                    "  - karštos (karštai rūkytos): 4 kg mėsos, 2 pakuotės.\n"
                    "  - šaltos (šaltai rūkytos): 5 kg mėsos, 2 pakuotės.\n"
                    "\nĮveskite 4 sveikus skaičius, atskirtus tarpais: virtos vytintos karštos saltos.\n"
                    "Pvz.: '2 1 0 3' (2 virtų, 1 vytinta, 0 karštų, 3 šaltų)\n"
                )
                klientoSoketas.sendall(paaiskinimas.encode('utf-8'))

                ats2 = klientoSoketas.recv(4096)
                if not ats2:
                    break
                cmd = ats2.decode('utf-8').strip()
                gam_result = gaminti_desras(zaidejas, cmd)
                klientoSoketas.sendall(gam_result.encode('utf-8'))



            elif komanda == "2":
                # 2 reiškia "Parduotuves" - t.y. pirkti_resursus
                # bet mums reikia sužinoti, ar pasirinks 1 ar 2 (Ūkininką ar pakuočių parduotuvę).
                # Taigi paprašome kliento pasirinkimo
                klaus = (
                    "Parduotuvių pasirinkimai:\n"
                    "1. Ūkininkas Antanas - Mėsos 10 kg už 10€\n"
                    "2. Pakuočių parduotuvė - 5 pakuotės už 5€\n"
                    "Pasirinkite parduotuvę (1 arba 2):\n"
                )
                klientoSoketas.sendall(klaus.encode('utf-8'))

                duomenys2 = klientoSoketas.recv(4096)
                if not duomenys2:
                    break
                parduotuve = duomenys2.decode('utf-8').strip()

                # Dabar kviečiame pirkti_resursus(zaidejas, parduotuve)
                ats_pard = pirkti_resursus(zaidejas, parduotuve)
                klientoSoketas.sendall(ats_pard.encode('utf-8'))

            elif komanda == "3":
                # Naujas užsakymas (keturių rūšių dešrų)
                txt = naujas_uzsakymas(zaidejas)
                klientoSoketas.sendall(txt.encode('utf-8'))


            elif komanda == "4":
                # Paklausti, kurį užsakymą vykdyti
                klientoSoketas.sendall(b"Kuri uzsakyma vykdyti? (1,2,3...)\n")
                ats4 = klientoSoketas.recv(4096)
                if not ats4:
                    break
                idx_str = ats4.decode('utf-8').strip()
                try:
                    idx = int(idx_str) - 1
                except ValueError:
                    klientoSoketas.sendall(b"Neteisingas indeksas!\n")
                    continue

                vyk_result = vykdyti_uzsakyma(zaidejas, idx)
                klientoSoketas.sendall(vyk_result.encode('utf-8'))


            else:
                klientoSoketas.sendall(b"Nezinoma komanda!\n")

            # ** Štai čia ** vėl atsiunčiame "visą meniu" atnaujintą
            # Atnaujiname meniu
            visas_meniu = suformuok_meniu(zaidejas)
            klientoSoketas.sendall(visas_meniu.encode('utf-8'))

        # 5. Išsaugome statistiką
        rasykStatistika(zaidejas)

    except Exception as e:
        print("Klaida valdykKlienta:", e)
    finally:
        klientoSoketas.close()

###############################################################################


def startuokServeri():
    if os.path.exists(SOKETO_FAILAS):
        os.remove(SOKETO_FAILAS)

    if not os.path.exists(ZAIDIMO_STATISTIKA):
        failas = open(ZAIDIMO_STATISTIKA, 'w')
        failas.write('Vardas;lygis;taskai;Testo pradžios laikas;Testo baigimo laikas\n')
        failas.close()

    serverioSoketas = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    serverioSoketas.bind(SOKETO_FAILAS)
    serverioSoketas.listen()

    print(f"Serveris įjungtas:  {SOKETO_FAILAS}")
    try:
        while True:
            klientoSoketas, _ = serverioSoketas.accept()
            print("Naujas klientas")
            valdykKlienta(klientoSoketas)
    except KeyboardInterrupt:
        print("\nServeris baigia darbą.")
    finally:
        serverioSoketas.close()
        os.remove(SOKETO_FAILAS)

if __name__ == "__main__":
    startuokServeri()
