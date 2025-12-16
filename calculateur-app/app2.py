# Pour run tu lances "streamlit run app2.py" dans ton terminal 

import streamlit as st
import pandas as pd

# Fonctions pour les calculs 
def calc_charges_sociales(brut_mensuel):
    # approximation: AVS/AI/APG/AC + cotisation LPP moyenne part salarié
    AVS = 0.0525
    AC = 0.011
    APG = 0.00225
    ANP = 0.02 # entre 1% et 3%
    #LPP_moyenne = 0.10  # entre 7% et 18% selon âge et plan

    return brut_mensuel * (AVS + AC + APG + ANP)

# Exemples de taux d'impôt moyen annuel par canton
CANTON_TAX_RATES = {
    "ZH (Zurich)": 0.09,
    "VD (Vaud)": 0,
    "GE (Genève)": 0.095,
    "BE (Berne)": 0.08,
    "VS (Valais)": 0.075,
    "Autre (taux moyen 9%)": 0.09
}

def calc_impots_mensuels(revenu_annuel_net, canton_key):
    taux = CANTON_TAX_RATES.get(canton_key, 0.09)
    # On prend par exemple +10%
    taux_prudent = taux * 1.10
    return (revenu_annuel_net * taux_prudent) / 12

##### A REVOIR #########
def revenu_imposable(revenu_annuel_net):
    # Simplification: on considère que le revenu imposable est le revenu net moins un abattement fixe
    abattement_fixe = 0  # CHF
    return max(revenu_annuel_net - abattement_fixe, 0)

def calc_impots_federal_direct(revenu_annuel_net):
    revenu_imposable_valeur = revenu_imposable(revenu_annuel_net)
    if revenu_imposable_valeur < 18500:
        impot = 0.0
    elif revenu_imposable_valeur <= 33200:
        impot = round((revenu_imposable_valeur -18500)/100) *  0.77 + 25.41
    elif revenu_imposable_valeur <= 43500:
        impot = round((revenu_imposable_valeur -33200)/100) *  0.88 + 108.54
    elif revenu_imposable_valeur <= 58000:
        impot = round((revenu_imposable_valeur -43500)/100) *  2.64 + 229.20
    elif revenu_imposable_valeur <= 76100:
        impot = round((revenu_imposable_valeur -58000)/100) *  2.97 + 612.00
    elif revenu_imposable_valeur <= 82000:
        impot = round((revenu_imposable_valeur -76100)/100) *  5.94 + 1149.55
    elif revenu_imposable_valeur <= 108800:
        impot = round((revenu_imposable_valeur -82000)/100) *  6.60 + 1500.00
    elif revenu_imposable_valeur <= 141500:
        impot = round((revenu_imposable_valeur -108800)/100) *  8.80 + 3268.80
    elif revenu_imposable_valeur <= 184900:
        impot = round((revenu_imposable_valeur -141500)/100) *  11.00 + 6146.40
    elif revenu_imposable_valeur <= 793300:
        impot = round((revenu_imposable_valeur -184900)/100) *  13.20 + 10920.40
    else:
        impot = round((revenu_imposable_valeur -793300)/100) *  11.50 + 91229.20
    return impot

def calc_impots_mensuels_vaud(revenu_annuel_net):
    # Exemple plus détaillé pour Vaud 
    revenu_imposable_valeur = revenu_imposable(revenu_annuel_net)
    if revenu_imposable_valeur <= 1600:
        taux = 0.01
    elif revenu_imposable_valeur <= 300000: 
        a = -4.88778071
        b = 1.13515927
        c = 0.21517791
        taux = (a + b * revenu_imposable_valeur**c) / 100
    elif revenu_imposable_valeur > 300000:
        supp = revenu_imposable_valeur - 300000
        taux_inf = 12.115
        taux_sup = 15.5 
        taux = (taux_sup + 300000/revenu_imposable_valeur * (taux_inf - taux_sup)) / 100
    impots_cant = revenu_imposable_valeur * taux / 12
    impots_cant_avec_coeff = impots_cant * 1.55 
    impots_comm = impots_cant * 0.75  # estimation coefficient communal moyen à 0.75
    impots = impots_cant_avec_coeff + impots_comm
    return impots

def calc_salaire_net(brut_mensuel, employeur_retention_percent=0.0):
    # employeur_retention_percent sert au cas ou l'employeur prend plus pour qqchose
    charges_sociales = calc_charges_sociales(brut_mensuel)
    return brut_mensuel - charges_sociales - (brut_mensuel * employeur_retention_percent)

# Interface Streamlit
st.set_page_config(page_title="Simulateur budget - Jeunes (Suisse)", layout="wide")
st.title("Simulateur de budget — Suisse")

with st.sidebar:
    st.header("Entrées de base")
    canton = st.selectbox("Canton (estimation impôts)", list(CANTON_TAX_RATES.keys()))
    age = st.number_input("Âge", min_value=15, max_value=80, value=24)
    situation = st.selectbox("Situation", ["Célibataire", "En couple (1 revenu)"])
    salaire_brut = st.number_input("Salaire brut mensuel (CHF)", min_value=0.0, value=3500.0, step=100.0)
    has_13e = st.checkbox("13e salaire (oui)", value=True)
    employeur_retention = st.number_input("Retenue employeur extra (%)", value=0.0, step=0.1)

st.header("Charges fixes mensuelles")
col1, col2 = st.columns(2)
with col1:
    prime_maladie = st.number_input("Prime maladie (CHF/mois)", min_value=0.0, value=350.0, step=10.0)
    loyer = st.number_input("Loyer (CHF/mois)", min_value=0.0, value=900.0, step=50.0)
    transports = st.number_input("Transports (CHF/mois)", min_value=0.0, value=80.0, step=10.0)
with col2:
    assurances_autres = st.number_input("Autres assurances (CHF/mois)", min_value=0.0, value=30.0, step=5.0)
    abonnements = st.number_input("Téléphone/Internet/Streaming (CHF/mois)", min_value=0.0, value=60.0, step=5.0)
    autres_charges = st.number_input("Autres charges (divers) (CHF/mois)", min_value=0.0, value=100.0, step=10.0)

st.markdown("---")
st.subheader("Scénarios / objectifs")
epargne_objectif = st.number_input("Objectif épargne mensuel (CHF)", min_value=0.0, value=200.0, step=10.0)
simulate_btn = st.button("Calculer le budget")

# Calculs et output
if simulate_btn:
    # ajustement pour 13e salaire
    facteur_13e = 12 / 13 if has_13e else 1.0
    salaire_brut_annuel = salaire_brut * 13 if has_13e else salaire_brut * 12
    salaire_net_annuel = calc_salaire_net(salaire_brut_annuel, employeur_retention/100.0)
    salaire_net_mensuel = salaire_net_annuel/13 if has_13e else salaire_net_annuel/12
    salaire_net = calc_salaire_net(salaire_brut, employeur_retention/100.0) * facteur_13e

    if canton == "VD (Vaud)":
        impots_cantonaux_mois = calc_impots_mensuels_vaud(salaire_net_annuel)
    else:
        impots_cantonaux_mois = calc_impots_mensuels(salaire_net_annuel, canton)

    charges_fixes = prime_maladie + loyer + transports + assurances_autres + abonnements + autres_charges + impots_cantonaux_mois
    
    reste_pour_vivre = salaire_net - charges_fixes - epargne_objectif

    impots_federaux_mois = calc_impots_federal_direct(salaire_net_annuel) / 12

    impots_total_annuel = (impots_cantonaux_mois + impots_federaux_mois) * 12

    impots_total_mensuels = impots_total_annuel / 12


    # Résumé
    st.subheader("Résumé mensuel estimé")
    df = pd.DataFrame({
        "Ligne": [
            "Salaire brut annuel estimé",
            "Salaire net annuel estimé",
            "Impôts communaux et cantonaux estimés (mensuel)",
            "Impôts communaux et cantonaux estimés (annuel)",
            "Impôts fédéraux estimés (mensuel)",
            "Impôts fédéraux estimés (annuel)",
            "Charges fixes (hors impôts)",
            "Objectif épargne mensuel",
            "Reste pour dépenses (alimentation, sorties, imprévus)",
            "Total impots annuels estimés",
            "Total impots mensuels estimés"
        ],
        "Montant (CHF/mois)": [
            round(salaire_brut_annuel, 0),
            round(salaire_net_annuel, 0),
            round(impots_cantonaux_mois, 0),
            round(impots_cantonaux_mois * 12, 0),
            round(impots_federaux_mois, 0),
            round(impots_federaux_mois * 12, 0),
            round(prime_maladie + loyer + transports + assurances_autres + abonnements + autres_charges, 0),
            round(epargne_objectif, 0),
            round(reste_pour_vivre, 0),
            round(impots_total_annuel, 0),
            round(impots_total_annuel / 12, 0)
        ]
    })
    st.table(df)

    # Indicateur de risque
    if reste_pour_vivre < 0:
        st.error(f"Attention : déficit de {abs(round(reste_pour_vivre,0))} CHF/mois. Réduire charges ou épargne.")
    elif reste_pour_vivre < 300:
        st.warning(f"Bas. Il te reste environ {round(reste_pour_vivre,0)} CHF/mois — marge faible.")
    else:
        st.success(f"OK. Il te reste environ {round(reste_pour_vivre,0)} CHF/mois pour vivre.")

    # Graphique
    st.subheader("Répartition mensuelle (estimation)")
    parts = {
        "Impôts": impots_total_mensuels,
        "Assurance santé": prime_maladie,
        "Loyer": loyer,
        "Transports": transports,
        "Autres fixes": assurances_autres + abonnements + autres_charges,
        "Epargne": epargne_objectif,
        "Reste dépenses": max(reste_pour_vivre, 0)
    }
    st.bar_chart(pd.Series(parts))
    st.markdown("**Remarque :** Les taux d'impôt sont des estimations simplifiées. Pour le calcul réel, il faut utiliser les barèmes cantonaux détaillés.")
