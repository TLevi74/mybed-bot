import discord
import random
from discord import app_commands

idezetek = [
    "Ott mondjuk hegy sem volt, de mostmár van - rajz tanár",
    "A lányok olyanok mint a fiúk csak fasz nélkül - Peti",
    "Ez egy kalap hülyeség - penzboti",
    "Ez az egész egy nagy lóvé - penzboti",
    "Ki hugyozott ide a kertembe!? - József",
    "Elég gyagya vagy - József apukája",
    "Túrós rudi - Csepei",
    "NA EZ EGY FREE FASZ! - penzboti",
    "Kérem szépen daddy-ke - penzboti",
    "Balfék osztály - Surányi",
    "Azt hittem hogy izé van rajtad... Batman - ének tanár",
    "Ajtókilincsesítünk - József",
    "Ez itt egy marék lófasz - penzboti",
    "Ez itt nem kocsma! - Hajzer",
    "Botond! Szent Efrém! - Hajzer",
    "Innentől a feladat megoldása pofon egyszerű... Magának nem! - Hajzer",
    "Minek agy?! Minek agy?! Szexelni kell meg enni. - penzboti",
    "Ha újraéledsz actually megbaszlak - penzboti",
    "Hogy ez egyik úgy bassza a másikat ahogyan a harmadik nem - Bulcsú elvtárs",
    "Persze hogy hatan vannak testvérek a Robiék, nem idén barnult le ő se. - Töri tanár",
    "Gyerekek, buzi vagyok. - Tar Levi",
    "Boti Magyarországon baszott csinos anyukákat szarik. - Ábel elvtárs",
    "Tanár úr, most heréket fogunk nézegetni? - Peti",
    "Mizuuu geciii - penzboti",
    "Egyetemen, aki jó egyetemre fog járni... De maguk nem fognak olyanba járni! - Hajzer",
    "Mutattam neked a faszmérő cetlit?! - Zsombi",
    "Dein Mutter! Mert hogy fiú. - penzboti",
    "A többi az szar mint a fos. - penzboti",
    "Ripi-ropi kis fityi-futyi. - Csattila",
    "I have no brain, I have potato - József",
    "Én gondolkodok, te meg kussolsz - Bulcsú elvtárs",
    "Levit meg mindenki megbaszhatja - penzboti",
    "Nem tudok nézni - Zsombi",
    "Nem bízunk a tanárok jóindulatában mert nincs ilyen. - Emőke",
    "Áramlik ez a szél aaaaa... A hogy is hívják felé no. - Csattila",
    "If you stuck in the desert then you would be hot. - Szabi",
]

@app_commands.command(name="quote", description="Random quote")
async def quote(interaction: discord.Interaction):
    await interaction.response.send_message(random.choice(idezetek))
