"""All health sentences shown to users, in English (en), Kannada (kn) and Hindi (hi).

English wording follows docs/health_advisory_reference.md exactly (CPCB [1], NCDC ASHA handbook [3], NCDC Health
Adaptation Plan [4], WHO [5]). Kannada and Hindi are DRAFT translations: have a native speaker check them before release.
Each entry: id -> {"src": "[n]", "en": ..., "kn": ..., "hi": ...}
"""

M = {
    # --- CPCB health impact statements, Table 3.12 [1] (headline) ---
    "impact_good": {"src": "[1]", "en": "Minimal Impact",
                    "kn": "ಕನಿಷ್ಠ ಪರಿಣಾಮ", "hi": "न्यूनतम प्रभाव"},
    "impact_satisfactory": {"src": "[1]", "en": "May cause minor breathing discomfort to sensitive people",
                            "kn": "ಸೂಕ್ಷ್ಮ ಜನರಿಗೆ ಸ್ವಲ್ಪ ಉಸಿರಾಟದ ತೊಂದರೆ ಉಂಟಾಗಬಹುದು",
                            "hi": "संवेदनशील लोगों को सांस लेने में हल्की परेशानी हो सकती है"},
    "impact_moderate": {"src": "[1]",
                        "en": "May cause breathing discomfort to the people with lung disease such as asthma and discomfort to people with heart disease, children and older adults",
                        "kn": "ಅಸ್ತಮಾದಂತಹ ಶ್ವಾಸಕೋಶ ಕಾಯಿಲೆ ಇರುವವರಿಗೆ ಉಸಿರಾಟದ ತೊಂದರೆ, ಹಾಗೂ ಹೃದಯ ಕಾಯಿಲೆ ಇರುವವರು, ಮಕ್ಕಳು ಮತ್ತು ವೃದ್ಧರಿಗೆ ಅಸ್ವಸ್ಥತೆ ಉಂಟಾಗಬಹುದು",
                        "hi": "अस्थमा जैसे फेफड़ों के रोग वाले लोगों को सांस लेने में परेशानी, और हृदय रोगियों, बच्चों तथा बुज़ुर्गों को असुविधा हो सकती है"},
    "impact_poor": {"src": "[1]",
                    "en": "May cause breathing discomfort to people on prolonged exposure and discomfort to people with heart disease with short exposure",
                    "kn": "ದೀರ್ಘಕಾಲ ಒಡ್ಡಿಕೊಂಡರೆ ಉಸಿರಾಟದ ತೊಂದರೆ, ಹೃದಯ ಕಾಯಿಲೆ ಇರುವವರಿಗೆ ಅಲ್ಪಕಾಲದಲ್ಲೇ ಅಸ್ವಸ್ಥತೆ ಉಂಟಾಗಬಹುದು",
                    "hi": "लंबे समय तक संपर्क में रहने पर सांस लेने में परेशानी, और हृदय रोगियों को थोड़े समय में ही असुविधा हो सकती है"},
    "impact_very_poor": {"src": "[1]",
                         "en": "May cause respiratory illness to the people on prolonged exposure. Effect may be more pronounced in people with lung and heart diseases",
                         "kn": "ದೀರ್ಘಕಾಲ ಒಡ್ಡಿಕೊಂಡರೆ ಉಸಿರಾಟದ ಕಾಯಿಲೆ ಉಂಟಾಗಬಹುದು. ಶ್ವಾಸಕೋಶ ಮತ್ತು ಹೃದಯ ಕಾಯಿಲೆ ಇರುವವರಲ್ಲಿ ಪರಿಣಾಮ ಹೆಚ್ಚಿರಬಹುದು",
                         "hi": "लंबे समय तक संपर्क में रहने पर श्वसन रोग हो सकता है। फेफड़ों और हृदय रोगियों पर असर अधिक हो सकता है"},
    "impact_severe": {"src": "[1]",
                      "en": "May cause respiratory effects even on healthy people and serious health impacts on people with lung/heart diseases. The health impacts may be experienced even during light physical activity",
                      "kn": "ಆರೋಗ್ಯವಂತರಲ್ಲೂ ಉಸಿರಾಟದ ಪರಿಣಾಮಗಳು ಮತ್ತು ಶ್ವಾಸಕೋಶ/ಹೃದಯ ಕಾಯಿಲೆ ಇರುವವರಲ್ಲಿ ಗಂಭೀರ ಆರೋಗ್ಯ ಪರಿಣಾಮಗಳು ಉಂಟಾಗಬಹುದು. ಲಘು ದೈಹಿಕ ಚಟುವಟಿಕೆಯಲ್ಲೂ ಪರಿಣಾಮ ಕಾಣಬಹುದು",
                      "hi": "स्वस्थ लोगों पर भी श्वसन प्रभाव और फेफड़े/हृदय रोगियों पर गंभीर स्वास्थ्य प्रभाव हो सकते हैं। हल्की शारीरिक गतिविधि में भी असर महसूस हो सकता है"},

    # --- NCDC category messages [3], general population ---
    "gen_good": {"src": "[3]", "en": "No special precautions", "kn": "ವಿಶೇಷ ಮುನ್ನೆಚ್ಚರಿಕೆ ಅಗತ್ಯವಿಲ್ಲ", "hi": "कोई विशेष सावधानी नहीं"},
    "gen_satisfactory": {"src": "[3]", "en": "No need for special precautions", "kn": "ವಿಶೇಷ ಮುನ್ನೆಚ್ಚರಿಕೆಯ ಅಗತ್ಯವಿಲ್ಲ", "hi": "विशेष सावधानी की आवश्यकता नहीं"},
    "gen_moderate": {"src": "[3]", "en": "Use mask or cloth to cover nose; avoid physical exertion for long periods",
                     "kn": "ಮೂಗು ಮುಚ್ಚಲು ಮಾಸ್ಕ್ ಅಥವಾ ಬಟ್ಟೆ ಬಳಸಿ; ದೀರ್ಘಕಾಲ ದೈಹಿಕ ಶ್ರಮ ತಪ್ಪಿಸಿ",
                     "hi": "नाक ढकने के लिए मास्क या कपड़े का उपयोग करें; लंबे समय तक शारीरिक मेहनत से बचें"},
    "gen_poor": {"src": "[3]", "en": "Avoid outdoor physical exertion, if possible; take frequent water breaks between work; use mask/cloth to cover nose while going out",
                 "kn": "ಸಾಧ್ಯವಾದರೆ ಹೊರಾಂಗಣ ದೈಹಿಕ ಶ್ರಮ ತಪ್ಪಿಸಿ; ಕೆಲಸದ ನಡುವೆ ಆಗಾಗ ನೀರು ಕುಡಿಯಿರಿ; ಹೊರಗೆ ಹೋಗುವಾಗ ಮಾಸ್ಕ್/ಬಟ್ಟೆಯಿಂದ ಮೂಗು ಮುಚ್ಚಿ",
                 "hi": "संभव हो तो बाहर शारीरिक मेहनत से बचें; काम के बीच बार-बार पानी पिएं; बाहर जाते समय मास्क/कपड़े से नाक ढकें"},
    "gen_very_poor": {"src": "[3]", "en": "Avoid outdoor physical activities; avoid additional pollution sources (burning, candles, smoking indoors); use a close-fitted N95 or N99 mask while going out",
                      "kn": "ಹೊರಾಂಗಣ ದೈಹಿಕ ಚಟುವಟಿಕೆ ತಪ್ಪಿಸಿ; ಹೆಚ್ಚುವರಿ ಮಾಲಿನ್ಯ ಮೂಲಗಳನ್ನು (ಸುಡುವುದು, ಮೇಣದಬತ್ತಿ, ಒಳಗೆ ಧೂಮಪಾನ) ತಪ್ಪಿಸಿ; ಹೊರಗೆ ಹೋಗುವಾಗ ಬಿಗಿಯಾದ N95 ಅಥವಾ N99 ಮಾಸ್ಕ್ ಬಳಸಿ",
                      "hi": "बाहरी शारीरिक गतिविधियों से बचें; अतिरिक्त प्रदूषण स्रोतों (जलाना, मोमबत्ती, घर में धूम्रपान) से बचें; बाहर जाते समय कसकर फिट N95 या N99 मास्क पहनें"},
    "gen_severe": {"src": "[3]", "en": "Avoid outdoor physical activities; use a close-fitted N95 or N99 mask while going out; avoid indoor pollution sources; drink lots of water",
                   "kn": "ಹೊರಾಂಗಣ ದೈಹಿಕ ಚಟುವಟಿಕೆ ತಪ್ಪಿಸಿ; ಹೊರಗೆ ಹೋಗುವಾಗ ಬಿಗಿಯಾದ N95 ಅಥವಾ N99 ಮಾಸ್ಕ್ ಬಳಸಿ; ಒಳಾಂಗಣ ಮಾಲಿನ್ಯ ಮೂಲಗಳನ್ನು ತಪ್ಪಿಸಿ; ಹೆಚ್ಚು ನೀರು ಕುಡಿಯಿರಿ",
                   "hi": "बाहरी शारीरिक गतिविधियों से बचें; बाहर जाते समय कसकर फिट N95 या N99 मास्क पहनें; घर के अंदर के प्रदूषण स्रोतों से बचें; खूब पानी पिएं"},

    # --- NCDC category messages [3], vulnerable population ---
    "vul_good": {"src": "[3]", "en": "No special precautions", "kn": "ವಿಶೇಷ ಮುನ್ನೆಚ್ಚರಿಕೆ ಅಗತ್ಯವಿಲ್ಲ", "hi": "कोई विशेष सावधानी नहीं"},
    "vul_satisfactory": {"src": "[3]", "en": "Use face masks/cloth/scarves to cover the nose while going out; avoid physical exertion for long periods",
                         "kn": "ಹೊರಗೆ ಹೋಗುವಾಗ ಮಾಸ್ಕ್/ಬಟ್ಟೆ/ಸ್ಕಾರ್ಫ್‌ನಿಂದ ಮೂಗು ಮುಚ್ಚಿ; ದೀರ್ಘಕಾಲ ದೈಹಿಕ ಶ್ರಮ ತಪ್ಪಿಸಿ",
                         "hi": "बाहर जाते समय मास्क/कपड़े/स्कार्फ से नाक ढकें; लंबे समय तक शारीरिक मेहनत से बचें"},
    "vul_moderate": {"src": "[3]", "en": "Use face masks/cloth/scarves to cover the nose while going out; avoid physical exertion for long periods; take frequent water breaks between work",
                     "kn": "ಹೊರಗೆ ಹೋಗುವಾಗ ಮಾಸ್ಕ್/ಬಟ್ಟೆ/ಸ್ಕಾರ್ಫ್‌ನಿಂದ ಮೂಗು ಮುಚ್ಚಿ; ದೀರ್ಘಕಾಲ ದೈಹಿಕ ಶ್ರಮ ತಪ್ಪಿಸಿ; ಕೆಲಸದ ನಡುವೆ ಆಗಾಗ ನೀರು ಕುಡಿಯಿರಿ",
                     "hi": "बाहर जाते समय मास्क/कपड़े/स्कार्फ से नाक ढकें; लंबे समय तक शारीरिक मेहनत से बचें; काम के बीच बार-बार पानी पिएं"},
    "vul_poor": {"src": "[3]", "en": "Use face masks/scarves to cover the nose while going out; avoid heavy exertion when outside and take lots of water breaks; in a closed space keep external doors and windows closed but ensure sufficient ventilation",
                 "kn": "ಹೊರಗೆ ಹೋಗುವಾಗ ಮಾಸ್ಕ್/ಸ್ಕಾರ್ಫ್‌ನಿಂದ ಮೂಗು ಮುಚ್ಚಿ; ಹೊರಗೆ ಭಾರಿ ಶ್ರಮ ತಪ್ಪಿಸಿ, ಆಗಾಗ ನೀರು ಕುಡಿಯಿರಿ; ಮುಚ್ಚಿದ ಸ್ಥಳದಲ್ಲಿ ಹೊರಗಿನ ಬಾಗಿಲು-ಕಿಟಕಿ ಮುಚ್ಚಿ, ಆದರೆ ಸಾಕಷ್ಟು ಗಾಳಿಯಾಡುವಂತೆ ನೋಡಿಕೊಳ್ಳಿ",
                 "hi": "बाहर जाते समय मास्क/स्कार्फ से नाक ढकें; बाहर भारी मेहनत से बचें और बार-बार पानी पिएं; बंद जगह में बाहरी दरवाज़े-खिड़कियां बंद रखें, पर पर्याप्त हवा का प्रवाह रखें"},
    "vul_very_poor": {"src": "[3]", "en": "Remain indoors as much as possible and keep activity levels low; use a close-fitted N95 or N99 mask while going out; take a healthy diet and lots of water; avoid indoor pollution sources",
                      "kn": "ಸಾಧ್ಯವಾದಷ್ಟು ಮನೆಯೊಳಗೇ ಇರಿ, ಚಟುವಟಿಕೆ ಕಡಿಮೆ ಮಾಡಿ; ಹೊರಗೆ ಹೋಗುವಾಗ ಬಿಗಿಯಾದ N95 ಅಥವಾ N99 ಮಾಸ್ಕ್ ಬಳಸಿ; ಆರೋಗ್ಯಕರ ಆಹಾರ ಮತ್ತು ಹೆಚ್ಚು ನೀರು ಸೇವಿಸಿ; ಒಳಾಂಗಣ ಮಾಲಿನ್ಯ ಮೂಲಗಳನ್ನು ತಪ್ಪಿಸಿ",
                      "hi": "जितना हो सके घर के अंदर रहें और गतिविधि कम रखें; बाहर जाते समय कसकर फिट N95 या N99 मास्क पहनें; स्वस्थ आहार लें और खूब पानी पिएं; घर के अंदर के प्रदूषण स्रोतों से बचें"},
    "vul_severe": {"src": "[3]", "en": "Remain indoors and keep activity levels low; avoid indoor pollution sources; always use a close-fitted N95 or N99 mask while stepping outside; step out only if urgent",
                   "kn": "ಮನೆಯೊಳಗೇ ಇರಿ, ಚಟುವಟಿಕೆ ಕಡಿಮೆ ಮಾಡಿ; ಒಳಾಂಗಣ ಮಾಲಿನ್ಯ ಮೂಲಗಳನ್ನು ತಪ್ಪಿಸಿ; ಹೊರಗೆ ಹೆಜ್ಜೆ ಇಡುವಾಗ ಯಾವಾಗಲೂ ಬಿಗಿಯಾದ N95 ಅಥವಾ N99 ಮಾಸ್ಕ್ ಬಳಸಿ; ತುರ್ತು ಇದ್ದರೆ ಮಾತ್ರ ಹೊರಗೆ ಹೋಗಿ",
                   "hi": "घर के अंदर रहें और गतिविधि कम रखें; घर के अंदर के प्रदूषण स्रोतों से बचें; बाहर निकलते समय हमेशा कसकर फिट N95 या N99 मास्क पहनें; केवल ज़रूरी होने पर ही बाहर जाएं"},

    # --- Group lines [4][5] ---
    "lh_meds": {"src": "[4]", "en": "Keep your prescribed medicines readily available and properly follow your doctor's instructions",
                "kn": "ವೈದ್ಯರು ಸೂಚಿಸಿದ ಔಷಧಿಗಳನ್ನು ಕೈಗೆಟುಕುವಂತೆ ಇಟ್ಟುಕೊಳ್ಳಿ ಮತ್ತು ವೈದ್ಯರ ಸೂಚನೆಗಳನ್ನು ಸರಿಯಾಗಿ ಪಾಲಿಸಿ",
                "hi": "डॉक्टर द्वारा बताई गई दवाएं पास रखें और डॉक्टर के निर्देशों का ठीक से पालन करें"},
    "lh_symptoms": {"src": "[4]", "en": "Keep a check on worsening symptoms and seek immediate medical advice if they get worse",
                    "kn": "ಲಕ್ಷಣಗಳು ಹೆಚ್ಚಾಗುತ್ತಿವೆಯೇ ಎಂದು ಗಮನಿಸಿ; ಹೆಚ್ಚಾದರೆ ತಕ್ಷಣ ವೈದ್ಯಕೀಯ ಸಲಹೆ ಪಡೆಯಿರಿ",
                    "hi": "लक्षण बढ़ने पर नज़र रखें और बिगड़ने पर तुरंत डॉक्टर की सलाह लें"},
    "vg_reduce": {"src": "[4]", "en": "Reduce prolonged or strenuous outdoor physical exertion",
                  "kn": "ದೀರ್ಘ ಅಥವಾ ಕಠಿಣ ಹೊರಾಂಗಣ ದೈಹಿಕ ಶ್ರಮವನ್ನು ಕಡಿಮೆ ಮಾಡಿ", "hi": "लंबी या कठिन बाहरी शारीरिक मेहनत कम करें"},
    "vg_avoid_prolonged": {"src": "[4]", "en": "Avoid prolonged or strenuous outdoor physical exertion",
                           "kn": "ದೀರ್ಘ ಅಥವಾ ಕಠಿಣ ಹೊರಾಂಗಣ ದೈಹಿಕ ಶ್ರಮವನ್ನು ತಪ್ಪಿಸಿ", "hi": "लंबी या कठिन बाहरी शारीरिक मेहनत से बचें"},
    "vg_avoid_outdoor": {"src": "[4]", "en": "Avoid outdoor physical activities",
                         "kn": "ಹೊರಾಂಗಣ ದೈಹಿಕ ಚಟುವಟಿಕೆಗಳನ್ನು ತಪ್ಪಿಸಿ", "hi": "बाहरी शारीरिक गतिविधियों से बचें"},
    "vg_indoors": {"src": "[4]", "en": "Remain indoors and keep activity levels low",
                   "kn": "ಮನೆಯೊಳಗೇ ಇರಿ ಮತ್ತು ಚಟುವಟಿಕೆ ಕಡಿಮೆ ಮಾಡಿ", "hi": "घर के अंदर रहें और गतिविधि कम रखें"},
    "preg_risk": {"src": "[5]", "en": "WHO lists pregnant women among the groups at higher risk from air pollution",
                  "kn": "ವಾಯು ಮಾಲಿನ್ಯದಿಂದ ಹೆಚ್ಚು ಅಪಾಯದಲ್ಲಿರುವ ಗುಂಪುಗಳಲ್ಲಿ ಗರ್ಭಿಣಿಯರನ್ನು WHO ಸೇರಿಸಿದೆ",
                  "hi": "WHO ने गर्भवती महिलाओं को वायु प्रदूषण से अधिक जोखिम वाले समूहों में रखा है"},
    "work_time": {"src": "[5]", "en": "Plan the best time and place for outdoor work",
                  "kn": "ಹೊರಾಂಗಣ ಕೆಲಸಕ್ಕೆ ಉತ್ತಮ ಸಮಯ ಮತ್ತು ಸ್ಥಳವನ್ನು ಯೋಜಿಸಿ", "hi": "बाहरी काम के लिए सबसे अच्छा समय और स्थान चुनें"},
    "work_water": {"src": "[3]", "en": "Take frequent water breaks between work",
                   "kn": "ಕೆಲಸದ ನಡುವೆ ಆಗಾಗ ನೀರು ಕುಡಿಯಿರಿ", "hi": "काम के बीच बार-बार पानी पिएं"},
    "ex_adapt": {"src": "[5]", "en": "Keep exercising, but adapt the timing and location of your exercise to reduce exposure",
                 "kn": "ವ್ಯಾಯಾಮ ಮುಂದುವರಿಸಿ, ಆದರೆ ಮಾಲಿನ್ಯ ಕಡಿಮೆ ಮಾಡಲು ಸಮಯ ಮತ್ತು ಸ್ಥಳವನ್ನು ಹೊಂದಿಸಿಕೊಳ್ಳಿ",
                 "hi": "व्यायाम जारी रखें, पर प्रदूषण से बचने के लिए समय और स्थान बदलें"},
    "ex_poor": {"src": "[4]", "en": "On days with poor to severe AQI, avoid outdoor morning and late evening walk, run, jog and physical exercise",
                "kn": "AQI ಕಳಪೆಯಿಂದ ತೀವ್ರ ಮಟ್ಟದ ದಿನಗಳಲ್ಲಿ ಬೆಳಗಿನ ಮತ್ತು ತಡ ಸಂಜೆಯ ಹೊರಾಂಗಣ ನಡಿಗೆ, ಓಟ, ಜಾಗಿಂಗ್ ಮತ್ತು ವ್ಯಾಯಾಮ ತಪ್ಪಿಸಿ",
                "hi": "खराब से गंभीर AQI वाले दिनों में सुबह और देर शाम बाहर टहलना, दौड़ना, जॉगिंग और व्यायाम न करें"},
    "doctor": {"src": "[4]", "en": "Consult the nearest doctor in case of breathlessness, giddiness, cough, chest discomfort or pain, irritation in the eyes",
               "kn": "ಉಸಿರಾಟದ ತೊಂದರೆ, ತಲೆಸುತ್ತು, ಕೆಮ್ಮು, ಎದೆ ನೋವು ಅಥವಾ ಕಣ್ಣಿನ ಉರಿ ಇದ್ದರೆ ಹತ್ತಿರದ ವೈದ್ಯರನ್ನು ಸಂಪರ್ಕಿಸಿ",
               "hi": "सांस फूलने, चक्कर, खांसी, सीने में तकलीफ या दर्द, आंखों में जलन होने पर नज़दीकी डॉक्टर से मिलें"},
    "who_child_resp": {"src": "[5]", "en": "There are no commercial respirators designed for children (based on information available as of February 2019)",
                       "kn": "ಮಕ್ಕಳಿಗಾಗಿ ವಿನ್ಯಾಸಗೊಳಿಸಿದ ವಾಣಿಜ್ಯ ರೆಸ್ಪಿರೇಟರ್‌ಗಳಿಲ್ಲ (ಫೆಬ್ರವರಿ 2019ರ ಮಾಹಿತಿ ಪ್ರಕಾರ)",
                       "hi": "बच्चों के लिए बने कोई व्यावसायिक रेस्पिरेटर नहीं हैं (फ़रवरी 2019 तक की जानकारी के अनुसार)"},
    "who_lh_resp": {"src": "[5]", "en": "WHO advises special caution with respirators for people with heart or lung disease",
                    "kn": "ಹೃದಯ ಅಥವಾ ಶ್ವಾಸಕೋಶ ಕಾಯಿಲೆ ಇರುವವರು ರೆಸ್ಪಿರೇಟರ್ ಬಳಸುವಾಗ ವಿಶೇಷ ಎಚ್ಚರಿಕೆ ವಹಿಸಬೇಕೆಂದು WHO ಸಲಹೆ ನೀಡುತ್ತದೆ",
                    "hi": "WHO हृदय या फेफड़ों के रोगियों को रेस्पिरेटर के उपयोग में विशेष सावधानी की सलाह देता है"},

    # --- Tips (one shown at a time) ---
    "tip_check": {"src": "[4]", "en": "Check the air quality index before leaving home", "kn": "ಮನೆಯಿಂದ ಹೊರಡುವ ಮೊದಲು ವಾಯು ಗುಣಮಟ್ಟ ಸೂಚ್ಯಂಕ ನೋಡಿ", "hi": "घर से निकलने से पहले वायु गुणवत्ता सूचकांक देखें"},
    "tip_traffic": {"src": "[4]", "en": "Avoid going to places with heavy traffic and congested areas", "kn": "ಭಾರೀ ಸಂಚಾರ ಮತ್ತು ಜನದಟ್ಟಣೆಯ ಪ್ರದೇಶಗಳಿಗೆ ಹೋಗುವುದನ್ನು ತಪ್ಪಿಸಿ", "hi": "भारी ट्रैफ़िक और भीड़भाड़ वाली जगहों पर जाने से बचें"},
    "tip_fuel": {"src": "[4]", "en": "Use clean smokeless fuels (gas or electricity) for cooking and heating", "kn": "ಅಡುಗೆ ಮತ್ತು ಬಿಸಿಮಾಡಲು ಶುದ್ಧ ಹೊಗೆರಹಿತ ಇಂಧನ (ಗ್ಯಾಸ್ ಅಥವಾ ವಿದ್ಯುತ್) ಬಳಸಿ", "hi": "खाना पकाने और गर्म करने के लिए स्वच्छ धुआं-रहित ईंधन (गैस या बिजली) का उपयोग करें"},
    "tip_burn": {"src": "[4]", "en": "Don't burn firecrackers, wood, leaves or garbage", "kn": "ಪಟಾಕಿ, ಕಟ್ಟಿಗೆ, ಎಲೆ ಅಥವಾ ಕಸವನ್ನು ಸುಡಬೇಡಿ", "hi": "पटाखे, लकड़ी, पत्ते या कचरा न जलाएं"},
    "tip_smoke": {"src": "[4]", "en": "Don't smoke cigarettes, bidis or other tobacco products", "kn": "ಸಿಗರೇಟ್, ಬೀಡಿ ಅಥವಾ ಇತರ ತಂಬಾಕು ಉತ್ಪನ್ನಗಳನ್ನು ಸೇದಬೇಡಿ", "hi": "सिगरेट, बीड़ी या अन्य तंबाकू उत्पादों का सेवन न करें"},
    "tip_windows": {"src": "[4]", "en": "Keep doors and windows closed in the early morning and late evening; ventilate in the afternoon (12 to 4 pm)", "kn": "ಮುಂಜಾನೆ ಮತ್ತು ತಡ ಸಂಜೆ ಬಾಗಿಲು-ಕಿಟಕಿ ಮುಚ್ಚಿ; ಮಧ್ಯಾಹ್ನ (12 ರಿಂದ 4) ಗಾಳಿಯಾಡಿಸಿ", "hi": "सुबह जल्दी और देर शाम दरवाज़े-खिड़कियां बंद रखें; दोपहर (12 से 4 बजे) हवा आने दें"},
    "tip_mop": {"src": "[4]", "en": "Practise wet mopping instead of sweeping", "kn": "ಗುಡಿಸುವ ಬದಲು ಒದ್ದೆ ಬಟ್ಟೆಯಿಂದ ಒರೆಸಿ", "hi": "झाड़ू की जगह गीला पोछा लगाएं"},
    "tip_coils": {"src": "[4]", "en": "Avoid burning mosquito coils and incense sticks in closed rooms", "kn": "ಮುಚ್ಚಿದ ಕೋಣೆಗಳಲ್ಲಿ ಸೊಳ್ಳೆ ಬತ್ತಿ ಮತ್ತು ಊದುಬತ್ತಿ ಹಚ್ಚಬೇಡಿ", "hi": "बंद कमरों में मच्छर कॉइल और अगरबत्ती न जलाएं"},
    "tip_cloth": {"src": "[3][4]", "en": "Paper masks, handkerchiefs, scarves and cloth are not effective in poor to severe pollution", "kn": "ಕಳಪೆಯಿಂದ ತೀವ್ರ ಮಾಲಿನ್ಯದಲ್ಲಿ ಕಾಗದದ ಮಾಸ್ಕ್, ಕರವಸ್ತ್ರ, ಸ್ಕಾರ್ಫ್ ಮತ್ತು ಬಟ್ಟೆ ಪರಿಣಾಮಕಾರಿಯಲ್ಲ", "hi": "खराब से गंभीर प्रदूषण में कागज़ के मास्क, रूमाल, स्कार्फ और कपड़ा असरदार नहीं होते"},
    "tip_eyes": {"src": "[4]", "en": "Keep washing your eyes with running water and gargle regularly with warm water", "kn": "ಹರಿಯುವ ನೀರಿನಿಂದ ಕಣ್ಣು ತೊಳೆಯುತ್ತಿರಿ ಮತ್ತು ಬೆಚ್ಚಗಿನ ನೀರಿನಿಂದ ಬಾಯಿ ಮುಕ್ಕಳಿಸಿ", "hi": "बहते पानी से आंखें धोते रहें और गुनगुने पानी से नियमित गरारे करें"},
    "tip_purifier": {"src": "[4][5]", "en": "If you use an air purifier, avoid one that works by generating ozone", "kn": "ಏರ್ ಪ್ಯೂರಿಫೈಯರ್ ಬಳಸಿದರೆ, ಓಝೋನ್ ಉತ್ಪಾದಿಸುವಂಥದ್ದನ್ನು ತಪ್ಪಿಸಿ", "hi": "एयर प्यूरीफ़ायर इस्तेमाल करें तो ओज़ोन बनाने वाले से बचें"},
    "tip_ac": {"src": "[4]", "en": "Use the air conditioner (home or car) in re-circulate mode", "kn": "ಏರ್ ಕಂಡಿಷನರ್ (ಮನೆ ಅಥವಾ ಕಾರು) ಅನ್ನು ರೀ-ಸರ್ಕ್ಯುಲೇಟ್ ಮೋಡ್‌ನಲ್ಲಿ ಬಳಸಿ", "hi": "एयर कंडीशनर (घर या कार) को री-सर्कुलेट मोड में चलाएं"},

    # --- Fixed texts ---
    "disclaimer": {"src": "", "en": "AirSathi forecasts are produced by a statistical model and can be wrong. Health messages are general guidance from CPCB, MoHFW and WHO, not medical advice. Follow your doctor's plan. Seek medical help if you have breathlessness, chest pain or dizziness. In an emergency, call 112.",
                   "kn": "AirSathi ಮುನ್ಸೂಚನೆಗಳು ಸಂಖ್ಯಾಶಾಸ್ತ್ರೀಯ ಮಾದರಿಯಿಂದ ಬರುತ್ತವೆ ಮತ್ತು ತಪ್ಪಾಗಿರಬಹುದು. ಆರೋಗ್ಯ ಸಂದೇಶಗಳು CPCB, MoHFW ಮತ್ತು WHO ನ ಸಾಮಾನ್ಯ ಮಾರ್ಗದರ್ಶನ, ವೈದ್ಯಕೀಯ ಸಲಹೆಯಲ್ಲ. ನಿಮ್ಮ ವೈದ್ಯರ ಸೂಚನೆ ಪಾಲಿಸಿ. ಉಸಿರಾಟದ ತೊಂದರೆ, ಎದೆ ನೋವು ಅಥವಾ ತಲೆಸುತ್ತು ಇದ್ದರೆ ವೈದ್ಯಕೀಯ ಸಹಾಯ ಪಡೆಯಿರಿ. ತುರ್ತು ಸಂದರ್ಭದಲ್ಲಿ 112 ಕರೆ ಮಾಡಿ.",
                   "hi": "AirSathi के पूर्वानुमान एक सांख्यिकीय मॉडल से बनते हैं और गलत हो सकते हैं। स्वास्थ्य संदेश CPCB, MoHFW और WHO के सामान्य दिशानिर्देश हैं, चिकित्सा सलाह नहीं। अपने डॉक्टर की योजना का पालन करें। सांस फूलने, सीने में दर्द या चक्कर आने पर चिकित्सा सहायता लें। आपात स्थिति में 112 पर कॉल करें।"},
}

SOURCES = {
    "[1]": "CPCB (2014) National Air Quality Index, CUPS/82/2014-15",
    "[3]": "NCDC (2024) Air pollution and its impact on health: Handbook for ASHA, MoHFW",
    "[4]": "NCDC (2021) Health adaptation plan for diseases due to air pollution, MoHFW",
    "[5]": "WHO (2024) Air pollution: Personal interventions and risk communication",
}


def t(msg_id, lang="en"):
    """Text of one message in the requested language (falls back to English)."""
    m = M[msg_id]
    return {"id": msg_id, "text": m.get(lang) or m["en"], "source": m["src"]}
