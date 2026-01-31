# Script de build EPUB avec chemins d'images corrigés
Write-Host "Démarrage de la conversion Pandoc..."

# Vérification de l'existence de Pandoc
if (-not (Get-Command pandoc -ErrorAction SilentlyContinue)) {
    Write-Error "Pandoc n'est pas trouvé dans le PATH. Veuillez l'installer et redémarrer."
    exit 1
}

$outputFile = "game-programming-patterns-fr.epub"

# Définir tous les chemins de ressources pour que Pandoc trouve les images
# Chaque chapitre a son propre dossier images/, donc on doit les inclure tous
$resourcePaths = @(
    ".",
    "book",
    "book\i-acknowledgements",
    "book\I-introduction\01-architecture-performance-and-games",
    "book\II-design-patterns-revisited\02-command",
    "book\II-design-patterns-revisited\03-flyweight",
    "book\II-design-patterns-revisited\04-observer",
    "book\II-design-patterns-revisited\05-prototype",
    "book\II-design-patterns-revisited\06-singleton",
    "book\II-design-patterns-revisited\07-state",
    "book\III-sequencing-patterns\08-double-buffer",
    "book\III-sequencing-patterns\09-game-loop",
    "book\III-sequencing-patterns\10-update-method",
    "book\IV-behavioral-patterns\11-bytecode",
    "book\IV-behavioral-patterns\12-subclass-sandbox",
    "book\IV-behavioral-patterns\13-type-object",
    "book\V-decoupling-patterns\14-component",
    "book\V-decoupling-patterns\15-event-queue",
    "book\V-decoupling-patterns\16-service-locator",
    "book\VI-optimization-patterns\17-data-locality",
    "book\VI-optimization-patterns\18-dirty-flag",
    "book\VI-optimization-patterns\19-object-pool",
    "book\VI-optimization-patterns\20-spatial-partition",
    "book\VI-optimization-patterns\21-aboutthe-book",
    "book\VI-optimization-patterns\22-nextchapter"
) -join ";"

# Commande Pandoc
pandoc `
    --metadata-file="metadata.yaml" `
    --epub-cover-image="cover.jpg" `
    --toc `
    --toc-depth=2 `
    --resource-path="$resourcePaths" `
    -o $outputFile `
    "book\i-acknowledgements\acknowledgements-fr.md" `
    "book\I-introduction\01-architecture-performance-and-games\architecture-performance-and-games-fr.md" `
    "book\II-design-patterns-revisited\02-command\command-fr.md" `
    "book\II-design-patterns-revisited\03-flyweight\flyweight-fr.md" `
    "book\II-design-patterns-revisited\04-observer\observer-fr.md" `
    "book\II-design-patterns-revisited\05-prototype\prototype-fr.md" `
    "book\II-design-patterns-revisited\06-singleton\singleton-fr.md" `
    "book\II-design-patterns-revisited\07-state\state-fr.md" `
    "book\III-sequencing-patterns\08-double-buffer\double-buffer-fr.md" `
    "book\III-sequencing-patterns\09-game-loop\game-loop-fr.md" `
    "book\III-sequencing-patterns\10-update-method\update-method-fr.md" `
    "book\IV-behavioral-patterns\11-bytecode\bytecode-fr.md" `
    "book\IV-behavioral-patterns\12-subclass-sandbox\subclass-sandbox-fr.md" `
    "book\IV-behavioral-patterns\13-type-object\type-object-fr.md" `
    "book\V-decoupling-patterns\14-component\component-fr.md" `
    "book\V-decoupling-patterns\15-event-queue\event-queue-fr.md" `
    "book\V-decoupling-patterns\16-service-locator\service-locator-fr.md" `
    "book\VI-optimization-patterns\17-data-locality\data-locality-fr.md" `
    "book\VI-optimization-patterns\18-dirty-flag\dirty-flag-fr.md" `
    "book\VI-optimization-patterns\19-object-pool\object-pool-fr.md" `
    "book\VI-optimization-patterns\20-spatial-partition\spatial-partition-fr.md" `
    "book\VI-optimization-patterns\21-aboutthe-book\aboutthe-book-fr.md" `
    "book\VI-optimization-patterns\22-nextchapter\nextchapter-fr.md"


if (Test-Path $outputFile) {
    $size = (Get-Item $outputFile).Length
    Write-Host "Succès ! EPUB généré : $outputFile ($size bytes)"
}
else {
    Write-Error "Erreur : Le fichier EPUB n'a pas été généré."
}
