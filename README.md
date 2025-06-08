
# ISOC Proiect: Microservices CLI pe GCP

## Structură
- `service_generator`: generează task-uri și le publică în Pub/Sub
- `service_processor`: ascultă Pub/Sub și salvează în Firestore

## Local
1. `docker-compose up --build`
2. Verifică log-urile pentru generator și processor

## În cloud (următorii pași)
1. Configurează GCP (Pub/Sub, Firestore, Artifact Registry)
2. Build & push imagini
3. Deploy pe Cloud Run
