import SwiftUI
import Combine

// MARK: - Models

enum Suit: String, CaseIterable {
    case clubs = "♣️"
    case diamonds = "♦️"
    case hearts = "♥️"
    case spades = "♠️"

    var name: String {
        switch self {
        case .clubs: return "Clubs"
        case .diamonds: return "Diamonds"
        case .hearts: return "Hearts"
        case .spades: return "Spades"
        }
    }
}

enum Rank: String, CaseIterable {
    case two = "2", three = "3", four = "4", five = "5"
    case six = "6", seven = "7", eight = "8", nine = "9"
    case ten = "10", jack = "J", queen = "Q", king = "K", ace = "A"

    var faceValue: Int {
        switch self {
        case .two: return 2
        case .three: return 3
        case .four: return 4
        case .five: return 5
        case .six: return 6
        case .seven: return 7
        case .eight: return 8
        case .nine: return 9
        case .ten: return 10
        case .jack: return 5
        case .queen: return 6
        case .king: return 7
        case .ace: return 8
        }
    }
}

struct Card: Identifiable, Equatable {
    let id = UUID()
    let suit: Suit
    let rank: Rank

    var displayName: String {
        "\(rank.rawValue)\(suit.rawValue)"
    }

    var faceValue: Int {
        rank.faceValue
    }
}

class Player: ObservableObject {
    let name: String
    @Published var hull: Int = 15
    @Published var shield: Int = 0
    @Published var hand: [Card] = []
    @Published var deck: [Card] = []
    @Published var discard: [Card] = []

    init(name: String) {
        self.name = name
        createStarterDeck()
    }

    private func createStarterDeck() {
        // 7 Engineers (2♣) and 3 Marines (2♠)
        deck = []
        for _ in 0..<7 {
            deck.append(Card(suit: .clubs, rank: .two))
        }
        for _ in 0..<3 {
            deck.append(Card(suit: .spades, rank: .two))
        }
        deck.shuffle()
    }

    func drawCards(_ count: Int) {
        for _ in 0..<count {
            if deck.isEmpty {
                deck = discard.shuffled()
                discard.removeAll()
            }
            if !deck.isEmpty {
                hand.append(deck.removeFirst())
            }
        }
    }

    func discardHand() {
        discard.append(contentsOf: hand)
        hand.removeAll()
    }

    func addToDiscard(_ card: Card) {
        discard.append(card)
    }
}

// MARK: - Game State

class GameState: ObservableObject {
    @Published var currentPlayer: Player
    @Published var opponent: Player
    @Published var techBay: [Card?] = Array(repeating: nil, count: 5)
    @Published var derelictCache: [Card] = []
    @Published var cacheDiscard: [Card] = []
    @Published var turnNumber = 1
    @Published var gamePhase = GamePhase.draw
    @Published var salvagePoints = 0
    @Published var spadesCount = 0
    @Published var heartsCount = 0
    @Published var gameLog: [String] = []
    @Published var isGameOver = false
    @Published var winner: String?
    @Published var techSearchCards: [Card] = []
    @Published var showTechSearch = false

    enum GamePhase {
        case draw, action, purchase, combat, end
    }

    init() {
        let player1 = Player(name: "Player 1")
        let player2 = Player(name: "AI")
        self.currentPlayer = player1
        self.opponent = player2
        setupGame()
    }

    private func setupGame() {
        // Create standard deck for derelict cache
        for suit in Suit.allCases {
            for rank in Rank.allCases {
                derelictCache.append(Card(suit: suit, rank: rank))
            }
        }
        derelictCache.shuffle()

        // Initialize tech bay
        for i in 0..<5 {
            techBay[i] = drawFromCache()
        }

        addLog("Game started! Each player has 15 hull.")
        startTurn()
    }

    func drawFromCache() -> Card? {
        if !derelictCache.isEmpty {
            return derelictCache.removeFirst()
        } else if !cacheDiscard.isEmpty {
            derelictCache = cacheDiscard.shuffled()
            cacheDiscard.removeAll()
            if !derelictCache.isEmpty {
                return derelictCache.removeFirst()
            }
        }
        return nil
    }

    func startTurn() {
        currentPlayer.shield = 0
        salvagePoints = 0
        spadesCount = 0
        heartsCount = 0

        addLog("\n--- Turn \(turnNumber): \(currentPlayer.name)'s turn ---")
        addLog("Hull: \(currentPlayer.hull) | Shield: \(currentPlayer.shield)")

        // Draw phase
        currentPlayer.drawCards(5)
        addLog("\(currentPlayer.name) draws 5 cards.")
        gamePhase = .action

        // If AI's turn, execute AI logic
        if currentPlayer.name == "AI" {
            executeAITurn()
        }
    }

    func playCard(_ card: Card, asResource: Bool) {
        guard let index = currentPlayer.hand.firstIndex(where: { $0.id == card.id }) else { return }
        currentPlayer.hand.remove(at: index)

        if asResource {
            salvagePoints += card.faceValue
            addLog("Used \(card.displayName) for resources (+\(card.faceValue) salvage).")
        } else {
            executeManeuver(card)
        }
    }

    private func executeManeuver(_ card: Card) {
        switch card.suit {
        case .clubs:
            addLog("Engineer maneuver: Drawing 1 card.")
            currentPlayer.drawCards(1)
        case .diamonds:
            addLog("Scientist maneuver: Tech search.")
            performTechSearch()
        case .hearts:
            heartsCount += 1
            addLog("Medic maneuver: Scheduled hull repair.")
        case .spades:
            spadesCount += 1
            addLog("Marine maneuver: Scheduled attack.")
        }
    }

    private func performTechSearch() {
        techSearchCards.removeAll()
        for _ in 0..<3 {
            if let card = drawFromCache() {
                techSearchCards.append(card)
            }
        }
        if !techSearchCards.isEmpty {
            showTechSearch = true
        } else {
            addLog("No cards available in Derelict Cache.")
        }
    }

    func selectTechSearchCard(_ card: Card) {
        currentPlayer.hand.append(card)
        addLog("Added \(card.displayName) to hand.")

        techSearchCards.removeAll(where: { $0.id == card.id })
        cacheDiscard.append(contentsOf: techSearchCards)
        techSearchCards.removeAll()
        showTechSearch = false
    }

    func endActionPhase() {
        gamePhase = .purchase
        addLog("Action phase complete. Salvage Points: \(salvagePoints)")
    }

    func purchaseTech(at index: Int) {
        guard let card = techBay[index] else { return }
        let cost = card.faceValue

        if salvagePoints >= cost {
            salvagePoints -= cost
            currentPlayer.addToDiscard(card)
            addLog("Purchased \(card.displayName) for \(cost) salvage.")
            techBay[index] = drawFromCache()
        }
    }

    func endPurchasePhase() {
        if salvagePoints > 0 {
            currentPlayer.shield += salvagePoints
            addLog("\(salvagePoints) salvage converted to shield.")
        }
        gamePhase = .combat
        resolveCombat()
    }

    private func resolveCombat() {
        // Attack resolution
        let damage = calculateAttackDamage()
        if damage > 0 {
            addLog("\(currentPlayer.name) attacks for \(damage) damage!")
            applyDamage(to: opponent, damage: damage)
        }

        // Repair resolution
        if heartsCount > 0 {
            let repair = calculateRepairAmount()
            currentPlayer.hull += repair
            addLog("\(currentPlayer.name) repairs \(repair) hull. New hull: \(currentPlayer.hull)")
        }

        // Check for game over
        if opponent.hull <= 0 || currentPlayer.hull <= 0 {
            endGame()
        } else {
            endTurn()
        }
    }

    private func calculateAttackDamage() -> Int {
        return (spadesCount * (spadesCount + 1)) / 2
    }

    private func calculateRepairAmount() -> Int {
        guard heartsCount > 0 else { return 0 }
        return 1 + (heartsCount - 1) * 2
    }

    private func applyDamage(to player: Player, damage: Int) {
        var remainingDamage = damage

        if player.shield > 0 {
            if player.shield >= remainingDamage {
                player.shield -= remainingDamage
                addLog("\(player.name)'s shield absorbed all damage.")
                remainingDamage = 0
            } else {
                addLog("\(player.name)'s shield absorbed \(player.shield) damage.")
                remainingDamage -= player.shield
                player.shield = 0
            }
        }

        if remainingDamage > 0 {
            player.hull -= remainingDamage
            addLog("\(player.name) takes \(remainingDamage) hull damage! Hull: \(player.hull)")
        }
    }

    private func endTurn() {
        currentPlayer.discardHand()

        // Switch players
        let temp = currentPlayer
        currentPlayer = opponent
        opponent = temp

        if currentPlayer.name == "Player 1" {
            turnNumber += 1
        }

        startTurn()
    }

    private func endGame() {
        isGameOver = true
        if currentPlayer.hull <= 0 && opponent.hull <= 0 {
            winner = "Draw!"
        } else if currentPlayer.hull <= 0 {
            winner = "\(opponent.name) wins!"
        } else {
            winner = "\(currentPlayer.name) wins!"
        }
        addLog("\n🎮 GAME OVER: \(winner ?? "Unknown")")
    }

    private func addLog(_ message: String) {
        gameLog.append(message)
    }

    // MARK: - AI Logic

    private func executeAITurn() {
        DispatchQueue.main.asyncAfter(deadline: .now() + 1) { [weak self] in
            self?.aiActionPhase()
        }
    }

    private func aiActionPhase() {
        // Simple AI: Play high-value cards as resources, low-value as maneuvers
        var cardsPlayed = 0
        let handCopy = currentPlayer.hand

        for card in handCopy {
            if cardsPlayed >= 3 { break } // Limit AI actions for speed

            if card.faceValue >= 6 {
                playCard(card, asResource: true)
            } else if card.suit == .spades {
                playCard(card, asResource: false)
            } else if card.suit == .hearts && currentPlayer.hull < 10 {
                playCard(card, asResource: false)
            } else {
                playCard(card, asResource: true)
            }
            cardsPlayed += 1
        }

        DispatchQueue.main.asyncAfter(deadline: .now() + 1) { [weak self] in
            self?.aiPurchasePhase()
        }
    }

    private func aiPurchasePhase() {
        endActionPhase()

        // AI tries to buy the most expensive card it can afford
        var bestIndex = -1
        var bestValue = 0

        for (index, card) in techBay.enumerated() {
            if let c = card, c.faceValue <= salvagePoints && c.faceValue > bestValue {
                bestIndex = index
                bestValue = c.faceValue
            }
        }

        if bestIndex >= 0 {
            purchaseTech(at: bestIndex)
        }

        DispatchQueue.main.asyncAfter(deadline: .now() + 1) { [weak self] in
            self?.endPurchasePhase()
        }
    }

    func resetGame() {
        let player1 = Player(name: "Player 1")
        let player2 = Player(name: "AI")
        self.currentPlayer = player1
        self.opponent = player2
        self.turnNumber = 1
        self.isGameOver = false
        self.winner = nil
        self.gameLog.removeAll()
        self.derelictCache.removeAll()
        self.cacheDiscard.removeAll()
        self.techBay = Array(repeating: nil, count: 5)
        setupGame()
    }
}

// MARK: - Views

struct ContentView: View {
    @StateObject private var gameState = GameState()

    var body: some View {
        ZStack {
            LinearGradient(colors: [.black, .blue.opacity(0.3)], startPoint: .top, endPoint: .bottom)
                .ignoresSafeArea()

            if gameState.isGameOver {
                GameOverView(gameState: gameState)
            } else {
                GameView(gameState: gameState)
            }
        }
    }
}

struct GameView: View {
    @ObservedObject var gameState: GameState
    @State private var selectedCard: Card?
    @State private var showActionSheet = false

    var body: some View {
        VStack(spacing: 0) {
            // Opponent status
            OpponentView(player: gameState.opponent)

            // Tech Bay
            TechBayView(gameState: gameState)

            // Game Log
            GameLogView(gameState: gameState)

            // Current Player Status
            CurrentPlayerView(player: gameState.currentPlayer, gameState: gameState)

            // Hand
            if gameState.currentPlayer.name != "AI" {
                HandView(gameState: gameState, selectedCard: $selectedCard, showActionSheet: $showActionSheet)
            }

            // Action Buttons
            if gameState.currentPlayer.name != "AI" {
                ActionButtonsView(gameState: gameState, selectedCard: $selectedCard)
            }
        }
        .sheet(isPresented: $gameState.showTechSearch) {
            TechSearchView(gameState: gameState)
        }
        .actionSheet(isPresented: $showActionSheet) {
            ActionSheet(
                title: Text("Play \(selectedCard?.displayName ?? "")"),
                buttons: [
                    .default(Text("As Resource (+\(selectedCard?.faceValue ?? 0) salvage)")) {
                        if let card = selectedCard {
                            gameState.playCard(card, asResource: true)
                        }
                    },
                    .default(Text("As Maneuver (\(getManeuverDescription(for: selectedCard)))")) {
                        if let card = selectedCard {
                            gameState.playCard(card, asResource: false)
                        }
                    },
                    .cancel()
                ]
            )
        }
    }

    func getManeuverDescription(for card: Card?) -> String {
        guard let card = card else { return "" }
        switch card.suit {
        case .clubs: return "Draw 1"
        case .diamonds: return "Tech Search"
        case .hearts: return "Repair"
        case .spades: return "Attack"
        }
    }
}

struct OpponentView: View {
    @ObservedObject var player: Player

    var body: some View {
        HStack {
            VStack(alignment: .leading) {
                Text(player.name)
                    .font(.headline)
                    .foregroundColor(.white)
                HStack {
                    Label("\(player.hull)", systemImage: "heart.fill")
                        .foregroundColor(.red)
                    Label("\(player.shield)", systemImage: "shield.fill")
                        .foregroundColor(.blue)
                }
            }
            Spacer()
            VStack(alignment: .trailing) {
                Text("Hand: \(player.hand.count)")
                Text("Deck: \(player.deck.count)")
            }
            .font(.caption)
            .foregroundColor(.gray)
        }
        .padding()
        .background(Color.black.opacity(0.5))
    }
}

struct TechBayView: View {
    @ObservedObject var gameState: GameState

    var body: some View {
        VStack(alignment: .leading) {
            Text("TECH BAY")
                .font(.caption)
                .foregroundColor(.yellow)
                .padding(.horizontal)

            ScrollView(.horizontal, showsIndicators: false) {
                HStack {
                    ForEach(0..<5) { index in
                        if let card = gameState.techBay[index] {
                            TechCardView(card: card, cost: card.faceValue) {
                                if gameState.gamePhase == .purchase &&
                                   gameState.salvagePoints >= card.faceValue &&
                                   gameState.currentPlayer.name != "AI" {
                                    gameState.purchaseTech(at: index)
                                }
                            }
                        } else {
                            RoundedRectangle(cornerRadius: 8)
                                .fill(Color.gray.opacity(0.3))
                                .frame(width: 60, height: 80)
                        }
                    }
                }
                .padding(.horizontal)
            }
        }
        .frame(height: 100)
    }
}

struct TechCardView: View {
    let card: Card
    let cost: Int
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack {
                Text(card.displayName)
                    .font(.title3)
                Text("💎 \(cost)")
                    .font(.caption)
                    .foregroundColor(.cyan)
            }
            .frame(width: 60, height: 80)
            .background(
                RoundedRectangle(cornerRadius: 8)
                    .fill(Color.blue.opacity(0.3))
                    .overlay(
                        RoundedRectangle(cornerRadius: 8)
                            .stroke(Color.cyan, lineWidth: 1)
                    )
            )
        }
    }
}

struct GameLogView: View {
    @ObservedObject var gameState: GameState

    var body: some View {
        ScrollViewReader { proxy in
            ScrollView {
                VStack(alignment: .leading, spacing: 2) {
                    ForEach(Array(gameState.gameLog.enumerated()), id: \.offset) { index, message in
                        Text(message)
                            .font(.system(size: 11, design: .monospaced))
                            .foregroundColor(.green)
                            .id(index)
                    }
                }
                .padding(8)
                .frame(maxWidth: .infinity, alignment: .leading)
            }
            .background(Color.black.opacity(0.7))
            .frame(height: 150)
            .onChange(of: gameState.gameLog.count) { _ in
                withAnimation {
                    proxy.scrollTo(gameState.gameLog.count - 1, anchor: .bottom)
                }
            }
        }
    }
}

struct CurrentPlayerView: View {
    @ObservedObject var player: Player
    @ObservedObject var gameState: GameState

    var body: some View {
        VStack {
            HStack {
                VStack(alignment: .leading) {
                    Text(player.name)
                        .font(.headline)
                        .foregroundColor(.white)
                    HStack {
                        Label("\(player.hull)", systemImage: "heart.fill")
                            .foregroundColor(.red)
                        Label("\(player.shield)", systemImage: "shield.fill")
                            .foregroundColor(.blue)
                    }
                }
                Spacer()
                VStack(alignment: .trailing) {
                    Text("Phase: \(phaseText)")
                        .font(.caption)
                    Text("Salvage: \(gameState.salvagePoints)")
                        .foregroundColor(.yellow)
                }
            }

            if gameState.spadesCount > 0 || gameState.heartsCount > 0 {
                HStack {
                    if gameState.spadesCount > 0 {
                        Label("\(gameState.spadesCount) Attack", systemImage: "bolt.fill")
                            .foregroundColor(.red)
                    }
                    if gameState.heartsCount > 0 {
                        Label("\(gameState.heartsCount) Repair", systemImage: "wrench.fill")
                            .foregroundColor(.green)
                    }
                }
                .font(.caption)
            }
        }
        .padding()
        .background(Color.black.opacity(0.5))
    }

    var phaseText: String {
        switch gameState.gamePhase {
        case .draw: return "Draw"
        case .action: return "Action"
        case .purchase: return "Purchase"
        case .combat: return "Combat"
        case .end: return "End"
        }
    }
}

struct HandView: View {
    @ObservedObject var gameState: GameState
    @Binding var selectedCard: Card?
    @Binding var showActionSheet: Bool

    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack {
                ForEach(gameState.currentPlayer.hand) { card in
                    CardView(card: card, isSelected: selectedCard?.id == card.id) {
                        if gameState.gamePhase == .action {
                            selectedCard = card
                            showActionSheet = true
                        }
                    }
                }
            }
            .padding()
        }
        .frame(height: 100)
        .background(Color.black.opacity(0.3))
    }
}

struct CardView: View {
    let card: Card
    let isSelected: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack {
                Text(card.displayName)
                    .font(.title2)
                Text("(\(card.faceValue))")
                    .font(.caption)
                    .foregroundColor(.gray)
            }
            .frame(width: 70, height: 90)
            .background(
                RoundedRectangle(cornerRadius: 10)
                    .fill(Color.white)
                    .overlay(
                        RoundedRectangle(cornerRadius: 10)
                            .stroke(isSelected ? Color.yellow : Color.gray, lineWidth: isSelected ? 3 : 1)
                    )
            )
            .shadow(radius: isSelected ? 5 : 2)
            .scaleEffect(isSelected ? 1.1 : 1.0)
        }
    }
}

struct ActionButtonsView: View {
    @ObservedObject var gameState: GameState
    @Binding var selectedCard: Card?

    var body: some View {
        HStack(spacing: 20) {
            if gameState.gamePhase == .action {
                Button("End Action Phase") {
                    gameState.endActionPhase()
                }
                .buttonStyle(GameButtonStyle(color: .orange))
            } else if gameState.gamePhase == .purchase {
                Button("End Purchase Phase") {
                    gameState.endPurchasePhase()
                }
                .buttonStyle(GameButtonStyle(color: .green))
            }
        }
        .padding()
    }
}

struct TechSearchView: View {
    @ObservedObject var gameState: GameState
    @Environment(\.presentationMode) var presentationMode

    var body: some View {
        VStack {
            Text("TECH SEARCH")
                .font(.title)
                .padding()

            Text("Choose one card to add to your hand:")
                .padding()

            HStack(spacing: 20) {
                ForEach(gameState.techSearchCards) { card in
                    CardView(card: card, isSelected: false) {
                        gameState.selectTechSearchCard(card)
                        presentationMode.wrappedValue.dismiss()
                    }
                }
            }
            .padding()

            Spacer()
        }
        .background(Color.black.opacity(0.9))
    }
}

struct GameOverView: View {
    @ObservedObject var gameState: GameState

    var body: some View {
        VStack(spacing: 30) {
            Text("GAME OVER")
                .font(.largeTitle)
                .foregroundColor(.yellow)

            Text(gameState.winner ?? "")
                .font(.title)
                .foregroundColor(.white)

            VStack(spacing: 10) {
                HStack {
                    Text("Player 1 Hull:")
                    Spacer()
                    Text("\(gameState.currentPlayer.name == "Player 1" ? gameState.currentPlayer.hull : gameState.opponent.hull)")
                }
                HStack {
                    Text("AI Hull:")
                    Spacer()
                    Text("\(gameState.currentPlayer.name == "AI" ? gameState.currentPlayer.hull : gameState.opponent.hull)")
                }
            }
            .padding()
            .background(Color.black.opacity(0.5))
            .cornerRadius(10)

            Button("New Game") {
                gameState.resetGame()
            }
            .buttonStyle(GameButtonStyle(color: .blue))
        }
        .padding()
    }
}

struct GameButtonStyle: ButtonStyle {
    let color: Color

    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .foregroundColor(.white)
            .padding(.horizontal, 30)
            .padding(.vertical, 15)
            .background(
                RoundedRectangle(cornerRadius: 10)
                    .fill(color)
                    .overlay(
                        RoundedRectangle(cornerRadius: 10)
                            .stroke(Color.white.opacity(0.3), lineWidth: 1)
                    )
            )
            .scaleEffect(configuration.isPressed ? 0.95 : 1.0)
    }
}

// MARK: - App Entry Point

@main
struct StarshipSalvageApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
                .preferredColorScheme(.dark)
        }
    }
}
