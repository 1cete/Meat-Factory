#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <cstdlib>
#include <ctime>
#include <thread>
#include <chrono>
#include <mutex>

#define SOKETO_FAILAS "./zaidimas.sock"
#define ZAIDIMO_STATISTIKA "./taskai.dat"

std::mutex mtx;

std::string dataLaikas(std::time_t dt) {
    char buffer[80];
    struct tm* timeinfo = localtime(&dt);
    strftime(buffer, sizeof(buffer), "%Y-%m-%d, %H:%M:%S", timeinfo);
    return std::string(buffer);
}

void rasykStatistika(const std::string& klientas) {
    std::ofstream file(ZAIDIMO_STATISTIKA, std::ios_base::app);
    if (file.is_open()) {
        file << klientas << "\n";
    }
}

class Uzsakymas {
public:
    int virtos = 0;
    int vytintos = 0;
    int karstos = 0;
    int saltos = 0;
    int laiko_trukme = 1;  // Paros skaičius
    int laiko_pradzia = 0;
    int delspinigiai = 0;
    int laiko_pabaiga = 0;
    bool ivykdytas = false;
    int pelnas = 0;

    Uzsakymas(int virtos = 0, int vytintos = 0, int karstos = 0, int saltos = 0, int laiko_trukme = 1)
        : virtos(virtos), vytintos(vytintos), karstos(karstos), saltos(saltos), laiko_trukme(laiko_trukme) {
        int total_count = virtos + vytintos + karstos + saltos;
        pelnas = total_count * 2;
    }

    void nustatyti_laiko_pabaiga(int laiko_pradzia) {
        laiko_pabaiga = laiko_pradzia + (laiko_trukme * 30);
    }

    void pridet_delspinigiai(int realus_praeje_laikas) {
        if (ivykdytas) return;
        if (realus_praeje_laikas >= laiko_pabaiga) {
            int velavimas = realus_praeje_laikas - laiko_pabaiga;
            if (velavimas > 0) {
                int intervalai = velavimas / 5;
                delspinigiai = intervalai * 1;
            }
        }
    }

    std::string toString() const {
        return "(virtos=" + std::to_string(virtos) + ", vytintos=" + std::to_string(vytintos) + ", karštos=" + std::to_string(karstos) + ", šaltos=" + std::to_string(saltos) + ", delspinigiai=" + std::to_string(delspinigiai) + ", ivykdytas=" + std::to_string(ivykdytas) + ")";
    }
};

class Klientas {
public:
    std::string vardas;
    int pinigai = 50;
    int mesa = 50;
    int pakuotes = 5;
    std::vector<Uzsakymas> uzsakymai;
    bool masina_sugedo = false;
    int reali_praejo_laikas = 0;
    std::time_t pradLaikas;
    std::time_t pabLaikas;

    int virtos = 0;
    int vytintos = 0;
    int karstos = 0;
    int saltos = 0;

    Klientas(const std::string& vardas) : vardas(vardas) {}

    std::string toString() const {
        return vardas + ";" + std::to_string(pinigai) + ";" + std::to_string(mesa) + ";" + std::to_string(pakuotes) + ";" + std::to_string(pradLaikas) + ";" + std::to_string(pabLaikas);
    }
};

std::string parodyti_uzsakymus(const Klientas& zaidejas) {
    if (zaidejas.uzsakymai.empty()) {
        return "Šiuo metu nėra užsakymų.\n";
    }
    std::string result;
    for (size_t i = 0; i < zaidejas.uzsakymai.size(); ++i) {
        const Uzsakymas& u = zaidejas.uzsakymai[i];
        int likusios_sekundes = std::max(u.laiko_pabaiga - zaidejas.reali_praejo_laikas, 0);
        int likusios_dienos = likusios_sekundes / 30;
        result += std::to_string(i + 1) + ") virtos: " + std::to_string(u.virtos) + ", vytintos: " + std::to_string(u.vytintos) + ", karštos: " + std::to_string(u.karstos) + ", šaltos: " + std::to_string(u.saltos) + ", Liko: " + std::to_string(likusios_dienos) + " d., delspinigiai: " + std::to_string(u.delspinigiai) + " €\nUž šį užsakymą gausite: " + std::to_string(u.pelnas) + " €\n";
    }
    return result + "\n";
}

std::string naujas_uzsakymas(Klientas& zaidejas) {
    int virtos = rand() % 11;
    int vytintos = rand() % 11;
    int karstos = rand() % 11;
    int saltos = rand() % 11;
    int laiko_trukme = rand() % 4 + 1;

    Uzsakymas u(virtos, vytintos, karstos, saltos, laiko_trukme);
    u.laiko_pradzia = zaidejas.reali_praejo_laikas;
    u.nustatyti_laiko_pabaiga(zaidejas.reali_praejo_laikas);

    zaidejas.uzsakymai.push_back(u);

    return "\nNaujas užsakymas: virtos: " + std::to_string(virtos) + ", vytintos: " + std::to_string(vytintos) + ", karštos: " + std::to_string(karstos) + ", šaltos: " + std::to_string(saltos) + "\nTrukmė: " + std::to_string(laiko_trukme) + " paros\nUž šį užsakymą gausite: " + std::to_string(u.pelnas) + " €\n";
}

std::string uzsakymu_sarasas_tekstu(const Klientas& zaidejas) {
    return parodyti_uzsakymus(zaidejas);
}

std::string pirkti_resursus(Klientas& zaidejas, const std::string& pasirinkimas) {
    std::string atsakymas = "Parduotuvių pasirinkimai:\n";
    atsakymas += "1. Ūkininkas Antanas - Mėsos 10 kg už 10€\n";
    atsakymas += "2. Pakuočių parduotuvė - 5 pakuotės už 5€\n";

    if (pasirinkimas == "1") {
        atsakymas += "                                                         .'T'. - -'.\n";
        atsakymas += "                                                      .'/|||||\\'. - -'.\n";
        atsakymas += "                                                    .'/|||||||||\\'. - -'.\n";
        atsakymas += "                                                  .'/|||||___|||||\\'. - -'.\n";
        atsakymas += "    Jūs pasirinkote ūkininką Antaną!             //|||||||||||||||||\\\\ - - \\\n";
        atsakymas += "                                                //|||||||||||||||||||\\\\ - - \\  /|\\   Perduok linkėjimus šeimai!!\n";
        atsakymas += "                                               //|||||||||||||||||||||\\\\_____/\\//|\\\\               .\n";
        atsakymas += "                                                |||||||||||||||||||||| |||||  //|\\\\                .\n";
        atsakymas += "                         ____________::___      ||||||||||ldb||||||||| ||||| ///|\\\\\\             _/V\\_ \n";
        atsakymas += "          _        _    /_)_)_)_)_)_)_)_)/\\     ||||| \\       // |||| ||||| ///|\\\\\\              (d_b) ,\n";
        atsakymas += "         ( )_    _( )  /_)_)_)_)_)_)_)_)/ _\\    |||||\\\\  /  (  - ) ||  || \\_ \\| |\n";
        atsakymas += "\n* Pateiktos priemonės vėliau realizuos paaiškinti argumentai.......";
        return atsakymas;
    }
    
    return "Neteisingas pasirinkimas.\n"; // <- ŠITAS būtinas
}
    
    void procesas(Klientas& zaidejas) {
        int pasirinkimas;
        bool baigti = false;
    
        while (!baigti) {
            std::cout << "\nPasirinkite veiksmą:\n";
            std::cout << "1. Patikrinti užsakymus\n";
            std::cout << "2. Padaryti naują užsakymą\n";
            std::cout << "3. Pirkti resursus\n";
            std::cout << "4. Išeiti\n";
            std::cout << "Jūsų pasirinkimas: ";
            std::cin >> pasirinkimas;
    
            switch (pasirinkimas) {
                case 1:
                    std::cout << uzsakymu_sarasas_tekstu(zaidejas);
                    break;
                case 2:
                    std::cout << naujas_uzsakymas(zaidejas);
                    break;
                case 3: {
                    std::string res_pasirinkimas;
                    std::cout << "Ką norite pirkti? (1 - Mėsos 10 kg, 2 - Pakuotes 5 vnt): ";
                    std::cin >> res_pasirinkimas;
                    std::cout << pirkti_resursus(zaidejas, res_pasirinkimas);
                    break;
                }
                case 4:
                    std::cout << "Išeinate iš žaidimo...\n";
                    baigti = true;
                    break;
                default:
                    std::cout << "Netinkamas pasirinkimas, bandykite dar kartą.\n";
                    break;
            }
    
            zaidejas.reali_praejo_laikas += 5;
            std::this_thread::sleep_for(std::chrono::seconds(5));
        }
    }
    
    int main() {
        srand(static_cast<unsigned int>(time(0))); // Atsitiktinių skaičių generatorius
    
        std::string vardas;
        std::cout << "Įveskite savo vardą: ";
        std::cin >> vardas;
    
        Klientas zaidejas(vardas);
    
        std::time_t now = std::time(0);
        zaidejas.pradLaikas = now;
        zaidejas.pabLaikas = now + 60 * 60 * 24;
    
        rasykStatistika(zaidejas.toString());
    
        procesas(zaidejas);
    
        return 0;
    }
