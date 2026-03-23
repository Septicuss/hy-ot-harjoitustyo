# HSL Sekvenssikaavio

```mermaid
sequenceDiagram

    participant main
    participant laitehallinto
    participant rautatietori
    participant ratikka6
    participant bussi244

    main->>laitehallinto: lisaa_lataaja(rautatietori)
    main->>laitehallinto: lisaa_lukija(ratikka6)
    main->>laitehallinto: lisaa_lukija(bussi244)

    create participant lippu_luukku
    main->>+lippu_luukku: osta_matkakortti("Kalle")
    create participant kallen_kortti
    lippu_luukku->>kallen_kortti: Matkakortti("Kalle")
    lippu_luukku-->>-main: kallen_kortti

    main->>rautatietori: lataa_arvoa(kallen_kortti, 3)
    rautatietori->>kallen_kortti: kasvata_arvoa(3)

    main->>ratikka6: osta_lippu(kallen_kortti, 0)
    ratikka6->>kallen_kortti: vahenna_arvoa(1.5)

    main->>bussi244: osta_lippu(kallen_kortti, 2)
    bussi244->>kallen_kortti: vahenna_arvoa(3.5)
```