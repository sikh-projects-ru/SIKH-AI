package org.ksd.sggsru

import android.content.Context
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.DrawerValue
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalDrawerSheet
import androidx.compose.material3.ModalNavigationDrawer
import androidx.compose.material3.NavigationDrawerItem
import androidx.compose.material3.NavigationDrawerItemDefaults
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.lightColorScheme
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.rememberDrawerState
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.foundation.layout.size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONArray
import org.json.JSONObject

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            SggsTheme {
                SggsApp()
            }
        }
    }
}

private object ReaderColors {
    val Page = Color(0xFFF8F5EE)
    val Surface = Color(0xFFFFFCF6)
    val Border = Color(0xFFE4D8C8)
    val Ink = Color(0xFF222222)
    val Muted = Color(0xFF66615A)
    val Gurmukhi = Color(0xFF550000)
    val Roman = Color(0xFF555555)
    val Translation = Color(0xFF005500)
    val Source = Color(0xFF5C3B20)
    val Rahao = Color(0xFF880044)
}

data class Manifest(
    val title: String,
    val angStart: Int,
    val angEnd: Int,
    val lineCount: Int,
)

data class Raag(
    val id: String,
    val order: Int,
    val nameRu: String,
    val nameGu: String,
    val type: String,
    val angStart: Int,
    val angEnd: Int,
)

data class Author(
    val id: String,
    val nameRu: String,
    val nameGu: String,
    val type: String,
    val mahalla: Int?,
    val angStart: Int,
    val angEnd: Int,
)

data class Work(
    val id: String,
    val titleRu: String,
    val titleGurmukhi: String,
    val raagId: String?,
    val angStart: Int,
    val angEnd: Int,
    val startShabadId: Int?,
    val shabadIdEnd: Int?,
    val startVerseId: Int?,
)

data class ShabadMeta(
    val shabadId: Int,
    val ang: Int,
    val raagId: String?,
    val authorId: String?,
)

data class SearchResult(
    val ang: Int,
    val shabadId: Int,
    val verseId: Int,
    val text: String,
)

data class Line(
    val verseId: Int,
    val isRahao: Boolean,
    val gurmukhi: String,
    val roman: String,
    val sahibSinghPa: String,
    val sahibSinghRu: String,
)

data class Shabad(
    val shabadId: Int,
    val rahaoVerseId: Int?,
    val lines: List<Line>,
)

data class Ang(
    val number: Int,
    val shabads: List<Shabad>,
)

data class Corpus(
    val manifest: Manifest,
    val raags: List<Raag>,
    val authors: List<Author>,
    val works: List<Work>,
    val shabads: List<ShabadMeta>,
    val about: String,
)

data class DisplaySettings(
    val showRoman: Boolean = true,
    val showPunjabi: Boolean = false,
    val showRussian: Boolean = true,
)

@Composable
fun SggsTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = lightColorScheme(
            primary = Color(0xFF4F3B2E),
            onPrimary = Color.White,
            secondary = Color(0xFF48624A),
            background = ReaderColors.Page,
            surface = ReaderColors.Surface,
            onSurface = ReaderColors.Ink,
        ),
        content = content,
    )
}

@Composable
fun SggsApp() {
    val context = LocalContext.current
    val corpusResult = remember { runCatching { loadCorpus(context) } }
    val corpus = corpusResult.getOrNull()

    var selectedAng by rememberSaveable { mutableIntStateOf(1) }
    var angInput by rememberSaveable { mutableStateOf("1") }
    var selectedRaagId by rememberSaveable { mutableStateOf<String?>(null) }
    var selectedAuthorId by rememberSaveable { mutableStateOf<String?>(null) }
    var selectedWorkId by rememberSaveable { mutableStateOf<String?>(null) }
    var showAbout by rememberSaveable { mutableStateOf(false) }
    var showSearch by rememberSaveable { mutableStateOf(false) }
    var highlightedVerseId by rememberSaveable { mutableStateOf<Int?>(null) }
    var settings by remember { mutableStateOf(DisplaySettings()) }
    val drawerState = rememberDrawerState(DrawerValue.Closed)
    val scope = rememberCoroutineScope()
    val listState = rememberLazyListState()

    val angResult = remember(selectedAng) {
        corpus?.let { runCatching { loadAng(context, selectedAng) } }
    }
    val currentAng = angResult?.getOrNull()

    LaunchedEffect(selectedAng, selectedRaagId, selectedAuthorId, selectedWorkId, showAbout) {
        angInput = selectedAng.toString()
        if (highlightedVerseId == null) {
            listState.scrollToItem(0)
        }
    }

    ModalNavigationDrawer(
        drawerState = drawerState,
        drawerContent = {
            if (corpus != null) {
                SggsDrawer(
                    corpus = corpus,
                    selectedRaagId = selectedRaagId,
                    selectedAuthorId = selectedAuthorId,
                    selectedWorkId = selectedWorkId,
                    showAbout = showAbout,
                    onShowAbout = {
                        showAbout = true
                        showSearch = false
                        selectedRaagId = null
                        selectedAuthorId = null
                        selectedWorkId = null
                        scope.launch { drawerState.close() }
                    },
                    onShowSearch = {
                        showSearch = true
                        showAbout = false
                        scope.launch { drawerState.close() }
                    },
                    onGoAng = { target ->
                        highlightedVerseId = null
                        selectedAng = target
                        selectedWorkId = null
                        selectedRaagId = null
                        selectedAuthorId = null
                        showAbout = false
                        showSearch = false
                        scope.launch { drawerState.close() }
                    },
                    onRaagSelected = { raag ->
                        showAbout = false
                        showSearch = false
                        highlightedVerseId = null
                        selectedRaagId = raag.id
                        selectedAuthorId = null
                        selectedWorkId = null
                        selectedAng = raag.angStart
                        scope.launch { drawerState.close() }
                    },
                    onAuthorSelected = { author ->
                        showAbout = false
                        showSearch = false
                        highlightedVerseId = null
                        selectedAuthorId = author.id
                        selectedRaagId = null
                        selectedWorkId = null
                        selectedAng = corpus.shabads.firstOrNull { it.authorId == author.id }?.ang ?: author.angStart
                        scope.launch { drawerState.close() }
                    },
                    onWorkSelected = { work ->
                        showAbout = false
                        showSearch = false
                        highlightedVerseId = work.startVerseId
                        selectedWorkId = work.id
                        selectedRaagId = null
                        selectedAuthorId = null
                        selectedAng = work.angStart
                        scope.launch { drawerState.close() }
                    },
                )
            }
        },
    ) {
        Scaffold(
            containerColor = ReaderColors.Page,
            topBar = {
                HeaderBar(
                    title = "Sri Guru Granth Sahib RU",
                    selectedAng = selectedAng,
                    subtitle = selectionSubtitle(corpus, selectedRaagId, selectedAuthorId, selectedWorkId),
                    onMenu = { scope.launch { drawerState.open() } },
                    onPrevious = {
                        val previousAng = previousFilteredAng(
                            corpus = corpus,
                            selectedAng = selectedAng,
                            selectedRaagId = selectedRaagId,
                            selectedAuthorId = selectedAuthorId,
                            selectedWorkId = selectedWorkId,
                        )
                        if (previousAng != null) {
                            highlightedVerseId = null
                            selectedAng = previousAng
                        }
                    },
                    onNext = {
                        val nextAng = nextFilteredAng(
                            corpus = corpus,
                            selectedAng = selectedAng,
                            selectedRaagId = selectedRaagId,
                            selectedAuthorId = selectedAuthorId,
                            selectedWorkId = selectedWorkId,
                        )
                        if (nextAng != null) {
                            highlightedVerseId = null
                            selectedAng = nextAng
                        }
                    },
                )
            },
        ) { padding ->
            when {
                corpus == null -> ErrorBox(
                    modifier = Modifier.padding(padding),
                    message = corpusResult.exceptionOrNull()?.message ?: "Не удалось открыть корпус",
                )
                showAbout -> LazyColumn(
                    modifier = Modifier.fillMaxSize().padding(padding),
                    contentPadding = PaddingValues(16.dp),
                ) {
                    item { MarkdownText(corpus.about) }
                }
                showSearch -> GlobalSearchScreen(
                    modifier = Modifier.fillMaxSize().padding(padding),
                    corpus = corpus,
                    selectedRaagId = selectedRaagId,
                    selectedAuthorId = selectedAuthorId,
                    selectedWorkId = selectedWorkId,
                    onOpenResult = { result ->
                        selectedRaagId = null
                        selectedAuthorId = null
                        selectedWorkId = null
                        selectedAng = result.ang
                        highlightedVerseId = result.verseId
                        showSearch = false
                        showAbout = false
                    },
                )
                currentAng == null -> ErrorBox(
                    modifier = Modifier.padding(padding),
                    message = angResult?.exceptionOrNull()?.message ?: "Не удалось открыть анг $selectedAng",
                )
                else -> {
                    val visibleShabads = filteredShabads(
                        ang = currentAng,
                        corpus = corpus,
                        selectedRaagId = selectedRaagId,
                        selectedAuthorId = selectedAuthorId,
                        selectedWorkId = selectedWorkId,
                        search = "",
                    )
                    LaunchedEffect(currentAng.number, highlightedVerseId, visibleShabads.size) {
                        val targetIndex = highlightedVerseId?.let { verseId ->
                            visibleShabads.indexOfFirst { item -> item.lines.any { it.verseId == verseId } }
                        } ?: -1
                        if (targetIndex >= 0) {
                            listState.scrollToItem(index = targetIndex + 1)
                        }
                    }
                    LazyColumn(
                        state = listState,
                        modifier = Modifier.fillMaxSize().padding(padding),
                        contentPadding = PaddingValues(16.dp),
                        verticalArrangement = Arrangement.spacedBy(12.dp),
                    ) {
                        item {
                            ReaderControls(
                                selectedAng = selectedAng,
                                angInput = angInput,
                                settings = settings,
                                currentRaag = corpus.raags.firstOrNull { selectedAng in it.angStart..it.angEnd },
                                contextSubtitle = selectionSubtitle(
                                    corpus = corpus,
                                    raagId = selectedRaagId,
                                    authorId = selectedAuthorId,
                                    workId = selectedWorkId,
                                ),
                                onAngInput = { angInput = it },
                                onGoAng = {
                                    val target = angInput.trim().toIntOrNull()
                                    if (target != null && target in 1..1430) {
                                        highlightedVerseId = null
                                        selectedAng = target
                                        selectedWorkId = null
                                        selectedRaagId = null
                                        selectedAuthorId = null
                                        showAbout = false
                                        showSearch = false
                                    }
                                },
                                onSettings = { settings = it },
                            )
                        }

                        items(visibleShabads, key = { it.shabad.shabadId }) { item ->
                            if (item.showWorkHeader && item.workTitle != null) {
                                WorkDivider(title = item.workTitle, subtitle = item.workSubtitle.orEmpty())
                            }
                            ShabadCard(item = item, settings = settings, highlightedVerseId = highlightedVerseId)
                        }
                    }
                }
            }
        }
    }
}

data class VisibleShabad(
    val shabad: Shabad,
    val raagName: String,
    val authorName: String,
    val workTitle: String?,
    val workSubtitle: String?,
    val showWorkHeader: Boolean,
    val lines: List<Line>,
)

@Composable
fun HeaderBar(
    title: String,
    selectedAng: Int,
    subtitle: String,
    onMenu: () -> Unit,
    onPrevious: () -> Unit,
    onNext: () -> Unit,
) {
    Surface(color = ReaderColors.Surface, shadowElevation = 2.dp) {
        Column(Modifier.fillMaxWidth().statusBarsPadding().padding(horizontal = 12.dp, vertical = 10.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Button(onClick = onMenu) { Text("Разделы") }
                Column(Modifier.weight(1f).padding(horizontal = 8.dp)) {
                    Text(title, fontWeight = FontWeight.SemiBold, color = ReaderColors.Ink)
                    Text("Анг $selectedAng" + if (subtitle.isBlank()) "" else " · $subtitle", color = ReaderColors.Muted, fontSize = 13.sp)
                }
                OutlinedButton(onClick = onPrevious, enabled = selectedAng > 1) { Text("‹") }
                Spacer(Modifier.width(6.dp))
                OutlinedButton(onClick = onNext, enabled = selectedAng < 1430) { Text("›") }
            }
        }
    }
}

@Composable
fun SggsDrawer(
    corpus: Corpus,
    selectedRaagId: String?,
    selectedAuthorId: String?,
    selectedWorkId: String?,
    showAbout: Boolean,
    onShowAbout: () -> Unit,
    onShowSearch: () -> Unit,
    onGoAng: (Int) -> Unit,
    onRaagSelected: (Raag) -> Unit,
    onAuthorSelected: (Author) -> Unit,
    onWorkSelected: (Work) -> Unit,
) {
    var showWorks by rememberSaveable { mutableStateOf(false) }
    var showRaags by rememberSaveable { mutableStateOf(false) }
    var showAuthors by rememberSaveable { mutableStateOf(false) }
    var angInput by rememberSaveable { mutableStateOf("") }

    fun goToAng() {
        val target = angInput.trim().toIntOrNull()
        if (target != null && target in corpus.manifest.angStart..corpus.manifest.angEnd) {
            onGoAng(target)
        }
    }

    ModalDrawerSheet(
        modifier = Modifier.width(330.dp),
        drawerContainerColor = ReaderColors.Surface,
    ) {
        LazyColumn(Modifier.fillMaxSize()) {
            item {
                Text(
                    "Sri Guru Granth Sahib RU",
                    modifier = Modifier.padding(20.dp, 20.dp, 20.dp, 4.dp),
                    fontSize = 20.sp,
                    fontWeight = FontWeight.SemiBold,
                )
                Text(
                    "${corpus.manifest.angStart}-${corpus.manifest.angEnd} анги · ${corpus.manifest.lineCount} строк",
                    modifier = Modifier.padding(horizontal = 20.dp),
                    color = ReaderColors.Muted,
                    fontSize = 13.sp,
                )
                DrawerSectionTitle("Перейти к ангу")
                Row(
                    modifier = Modifier.padding(horizontal = 12.dp, vertical = 4.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    OutlinedTextField(
                        value = angInput,
                        onValueChange = { angInput = it },
                        label = { Text("Анг (1–${corpus.manifest.angEnd})") },
                        modifier = Modifier.weight(1f),
                        singleLine = true,
                        keyboardOptions = KeyboardOptions(
                            keyboardType = KeyboardType.Number,
                            imeAction = ImeAction.Go,
                        ),
                        keyboardActions = KeyboardActions(onGo = { goToAng() }),
                    )
                    Spacer(Modifier.width(8.dp))
                    OutlinedButton(onClick = { goToAng() }) { Text("→") }
                }
                DrawerSectionTitle("Информация")
                DrawerItem("О переводе", showAbout, onClick = onShowAbout)
                DrawerItem("Поиск", false, subtitle = "По русскому тексту", onClick = onShowSearch)
                DrawerSectionToggle("Произведения", showWorks) { showWorks = !showWorks }
            }
            if (showWorks) {
                items(corpus.works, key = { it.id }) { work ->
                    DrawerItem(
                        title = "${work.titleRu} · ${work.angStart}-${work.angEnd}",
                        selected = selectedWorkId == work.id,
                        subtitle = work.titleGurmukhi,
                        onClick = { onWorkSelected(work) },
                    )
                }
            }
            item { DrawerSectionToggle("Раги и разделы", showRaags) { showRaags = !showRaags } }
            if (showRaags) {
                items(corpus.raags, key = { it.id }) { raag ->
                    DrawerItem(
                        title = "${raag.nameRu} · ${raag.angStart}-${raag.angEnd}",
                        selected = selectedRaagId == raag.id,
                        subtitle = raag.nameGu,
                        onClick = { onRaagSelected(raag) },
                    )
                }
            }
            item { DrawerSectionToggle("Авторы", showAuthors) { showAuthors = !showAuthors } }
            if (showAuthors) {
                items(corpus.authors, key = { it.id }) { author ->
                    DrawerItem(
                        title = author.nameRu,
                        selected = selectedAuthorId == author.id,
                        subtitle = author.nameGu,
                        onClick = { onAuthorSelected(author) },
                    )
                }
            }
        }
    }
}

@Composable
fun DrawerSectionTitle(text: String) {
    Text(
        text = text,
        modifier = Modifier.padding(horizontal = 20.dp, vertical = 10.dp),
        color = ReaderColors.Muted,
        fontSize = 13.sp,
        fontWeight = FontWeight.SemiBold,
    )
}

@Composable
fun DrawerSectionToggle(text: String, expanded: Boolean, onClick: () -> Unit) {
    TextButton(
        onClick = onClick,
        modifier = Modifier.fillMaxWidth().padding(horizontal = 8.dp),
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text(text, fontWeight = FontWeight.SemiBold)
            Text(if (expanded) "Свернуть" else "Открыть", color = ReaderColors.Muted, fontSize = 13.sp)
        }
    }
}

@Composable
fun DrawerItem(title: String, selected: Boolean, subtitle: String = "", onClick: () -> Unit) {
    NavigationDrawerItem(
        label = {
            Column {
                Text(title)
                if (subtitle.isNotBlank()) {
                    Text(subtitle, color = ReaderColors.Gurmukhi, fontSize = 13.sp)
                }
            }
        },
        selected = selected,
        colors = NavigationDrawerItemDefaults.colors(
            selectedContainerColor = Color(0xFFECE0D3),
            unselectedContainerColor = ReaderColors.Surface,
            selectedTextColor = ReaderColors.Ink,
            unselectedTextColor = ReaderColors.Ink,
        ),
        onClick = onClick,
        modifier = Modifier.padding(horizontal = 12.dp),
    )
}

@Composable
fun ReaderControls(
    selectedAng: Int,
    angInput: String,
    settings: DisplaySettings,
    currentRaag: Raag?,
    contextSubtitle: String,
    onAngInput: (String) -> Unit,
    onGoAng: () -> Unit,
    onSettings: (DisplaySettings) -> Unit,
) {
    Card(
        colors = CardDefaults.cardColors(containerColor = ReaderColors.Surface),
        border = BorderStroke(1.dp, ReaderColors.Border),
        shape = RoundedCornerShape(8.dp),
    ) {
        Column(Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Text(
                text = buildReaderTitle(currentRaag, selectedAng, contextSubtitle),
                fontWeight = FontWeight.SemiBold,
                color = ReaderColors.Ink,
            )
            Row(verticalAlignment = Alignment.CenterVertically) {
                OutlinedTextField(
                    value = angInput,
                    onValueChange = onAngInput,
                    label = { Text("Анг") },
                    modifier = Modifier.weight(1f),
                    singleLine = true,
                    keyboardOptions = KeyboardOptions(
                        keyboardType = KeyboardType.Number,
                        imeAction = ImeAction.Go,
                    ),
                    keyboardActions = KeyboardActions(onGo = { onGoAng() }),
                )
                Spacer(Modifier.width(8.dp))
                OutlinedButton(onClick = onGoAng) { Text("Открыть") }
            }
            // TODO: Restore current-ang search if it becomes useful in the reader flow.
            ToggleRow("Транслитерация", settings.showRoman) { onSettings(settings.copy(showRoman = it)) }
            ToggleRow("Сахиб Сингх Панджаби", settings.showPunjabi) { onSettings(settings.copy(showPunjabi = it)) }
            ToggleRow("Перевод на русский", settings.showRussian) { onSettings(settings.copy(showRussian = it)) }
        }
    }
}

@Composable
fun ToggleRow(label: String, checked: Boolean, onChange: (Boolean) -> Unit) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(label, color = ReaderColors.Ink)
        Switch(checked = checked, onCheckedChange = onChange)
    }
}

@Composable
fun ShabadCard(item: VisibleShabad, settings: DisplaySettings, highlightedVerseId: Int?) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = ReaderColors.Surface),
        border = BorderStroke(1.dp, ReaderColors.Border),
        shape = RoundedCornerShape(8.dp),
    ) {
        Column(Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Text(
                "Шабд ${item.shabad.shabadId} · ${item.raagName} · ${item.authorName}",
                color = ReaderColors.Muted,
                fontSize = 13.sp,
            )
            item.lines.forEach { line ->
                LineBlock(line = line, settings = settings, highlighted = line.verseId == highlightedVerseId)
            }
        }
    }
}

@Composable
fun LineBlock(line: Line, settings: DisplaySettings, highlighted: Boolean) {
    val border = when {
        highlighted -> ReaderColors.Translation
        line.isRahao -> ReaderColors.Rahao
        else -> ReaderColors.Border
    }
    val container = if (highlighted) Color(0xFFEAF4E8) else Color.Transparent
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = container),
        border = BorderStroke(1.dp, border),
        shape = RoundedCornerShape(8.dp),
    ) {
        Column(Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
            Text(
                text = line.gurmukhi,
                color = if (line.isRahao) ReaderColors.Rahao else ReaderColors.Gurmukhi,
                fontSize = 20.sp,
                lineHeight = 28.sp,
                fontWeight = if (line.isRahao) FontWeight.SemiBold else FontWeight.Normal,
            )
            if (settings.showRoman && line.roman.isNotBlank()) {
                Text(line.roman, color = ReaderColors.Roman, fontSize = 14.sp)
            }
            if (settings.showRussian && line.sahibSinghRu.isNotBlank()) {
                Text(line.sahibSinghRu, color = ReaderColors.Translation, fontSize = 16.sp, lineHeight = 23.sp)
            }
            if (settings.showPunjabi && line.sahibSinghPa.isNotBlank()) {
                Text(line.sahibSinghPa, color = ReaderColors.Source, fontSize = 15.sp, lineHeight = 22.sp)
            }
            Text("строка ${line.verseId}", color = ReaderColors.Muted, fontSize = 11.sp)
        }
    }
}

@Composable
fun WorkDivider(title: String, subtitle: String) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        color = Color(0xFFECE0D3),
        shape = RoundedCornerShape(8.dp),
        border = BorderStroke(1.dp, ReaderColors.Border),
    ) {
        Column(Modifier.padding(horizontal = 14.dp, vertical = 10.dp), verticalArrangement = Arrangement.spacedBy(2.dp)) {
            Text(title, color = ReaderColors.Ink, fontWeight = FontWeight.SemiBold)
            if (subtitle.isNotBlank()) {
                Text(subtitle, color = ReaderColors.Gurmukhi, fontSize = 13.sp)
            }
        }
    }
}

@Composable
fun GlobalSearchScreen(
    modifier: Modifier = Modifier,
    corpus: Corpus,
    selectedRaagId: String?,
    selectedAuthorId: String?,
    selectedWorkId: String?,
    onOpenResult: (SearchResult) -> Unit,
) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    var query by rememberSaveable { mutableStateOf("") }
    var searchedQuery by rememberSaveable { mutableStateOf("") }
    var page by rememberSaveable { mutableIntStateOf(0) }
    var loading by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }
    var results by remember { mutableStateOf<List<SearchResult>>(emptyList()) }
    val pageSize = 20
    val shabadMeta = remember(corpus.shabads) { corpus.shabads.associateBy { it.shabadId } }
    val pageCount = if (results.isEmpty()) 0 else ((results.size - 1) / pageSize) + 1
    val pageResults = results.drop(page * pageSize).take(pageSize)
    val activeScope = searchScopeSummary(corpus, selectedRaagId, selectedAuthorId, selectedWorkId)

    fun runSearch() {
        val q = query.trim()
        if (q.length < 2 || loading) return
        loading = true
        error = null
        searchedQuery = q
        page = 0
        scope.launch {
            val searchResult = runCatching {
                withContext(Dispatchers.IO) {
                    searchRussianText(context = context, corpus = corpus, query = q)
                }
            }
            loading = false
            searchResult
                .onSuccess {
                    results = filterSearchResults(
                        corpus = corpus,
                        shabadMeta = shabadMeta,
                        results = it,
                        selectedRaagId = selectedRaagId,
                        selectedAuthorId = selectedAuthorId,
                        selectedWorkId = selectedWorkId,
                    )
                }
                .onFailure {
                    results = emptyList()
                    error = it.message ?: "Не удалось выполнить поиск"
                }
        }
    }

    LazyColumn(
        modifier = modifier,
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = ReaderColors.Surface),
                border = BorderStroke(1.dp, ReaderColors.Border),
                shape = RoundedCornerShape(8.dp),
            ) {
                Column(Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    Text("Поиск", fontWeight = FontWeight.SemiBold, color = ReaderColors.Ink)
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        OutlinedTextField(
                            value = query,
                            onValueChange = { query = it },
                            label = { Text("Русский текст") },
                            modifier = Modifier.weight(1f),
                            singleLine = true,
                        )
                        Spacer(Modifier.width(8.dp))
                        Button(onClick = { runSearch() }, enabled = query.trim().length >= 2 && !loading) {
                            if (loading) {
                                CircularProgressIndicator(
                                    modifier = Modifier.size(18.dp),
                                    strokeWidth = 2.dp,
                                    color = ReaderColors.Surface,
                                )
                            } else {
                                Text("Найти")
                            }
                        }
                    }
                    if (activeScope.isNotBlank()) {
                        Text("Контекст: $activeScope", color = ReaderColors.Muted, fontSize = 13.sp)
                    }
                    if (loading) {
                        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            CircularProgressIndicator(modifier = Modifier.size(16.dp), strokeWidth = 2.dp)
                            Text(
                                "Поиск по ангам ${corpus.manifest.angStart}–${corpus.manifest.angEnd}…",
                                color = ReaderColors.Muted,
                                fontSize = 13.sp,
                            )
                        }
                    } else {
                        val status = when {
                            error != null -> error.orEmpty()
                            searchedQuery.isBlank() -> "Введите минимум 2 символа."
                            results.isEmpty() -> "Ничего не найдено."
                            else -> "Найдено: ${results.size} · страница ${page + 1} из $pageCount"
                        }
                        Text(status, color = if (error != null) ReaderColors.Rahao else ReaderColors.Muted, fontSize = 13.sp)
                    }
                }
            }
        }

        items(pageResults, key = { "${it.ang}:${it.shabadId}:${it.verseId}" }) { result ->
            SearchResultCard(result = result, onClick = { onOpenResult(result) })
        }

        if (pageCount > 1) {
            item {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    OutlinedButton(onClick = { if (page > 0) page -= 1 }, enabled = page > 0) {
                        Text("Назад")
                    }
                    Text("${page + 1} / $pageCount", color = ReaderColors.Muted)
                    OutlinedButton(onClick = { if (page < pageCount - 1) page += 1 }, enabled = page < pageCount - 1) {
                        Text("Дальше")
                    }
                }
            }
        }
    }
}

@Composable
fun SearchResultCard(result: SearchResult, onClick: () -> Unit) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = ReaderColors.Surface),
        border = BorderStroke(1.dp, ReaderColors.Border),
        shape = RoundedCornerShape(8.dp),
        onClick = onClick,
    ) {
        Column(Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
            Text(
                "Анг ${result.ang} · Шабд ${result.shabadId} · строка ${result.verseId}",
                color = ReaderColors.Muted,
                fontSize = 13.sp,
            )
            Text(result.text, color = ReaderColors.Translation, fontSize = 16.sp, lineHeight = 23.sp)
        }
    }
}

@Composable
fun MarkdownText(markdown: String) {
    Card(
        colors = CardDefaults.cardColors(containerColor = ReaderColors.Surface),
        border = BorderStroke(1.dp, ReaderColors.Border),
        shape = RoundedCornerShape(8.dp),
    ) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            markdown.lines().forEach { raw ->
                val line = raw.trim()
                when {
                    line.startsWith("# ") -> Text(line.removePrefix("# "), fontSize = 22.sp, fontWeight = FontWeight.Bold)
                    line.isBlank() -> Spacer(Modifier.height(4.dp))
                    else -> Text(line, color = ReaderColors.Ink, lineHeight = 22.sp)
                }
            }
        }
    }
}

@Composable
fun ErrorBox(modifier: Modifier = Modifier, message: String) {
    Box(modifier = modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
        Text(message, color = ReaderColors.Rahao)
    }
}

fun filteredShabads(
    ang: Ang,
    corpus: Corpus,
    selectedRaagId: String?,
    selectedAuthorId: String?,
    selectedWorkId: String?,
    search: String,
): List<VisibleShabad> {
    val shabadMeta = corpus.shabads.associateBy { it.shabadId }
    val raags = corpus.raags.associateBy { it.id }
    val authors = corpus.authors.associateBy { it.id }
    val work = selectedWorkId?.let { id -> corpus.works.firstOrNull { it.id == id } }
    val worksByRaag = corpus.works
        .filter { it.raagId != null }
        .associateBy { it.raagId }
    val q = search.trim().lowercase()

    val visible = ang.shabads.mapNotNull { shabad ->
        val meta = shabadMeta[shabad.shabadId]
        if (selectedRaagId != null && meta?.raagId != selectedRaagId) return@mapNotNull null
        if (selectedAuthorId != null && meta?.authorId != selectedAuthorId) return@mapNotNull null
        if (work != null) {
            if (work.raagId != null && meta?.raagId != work.raagId) return@mapNotNull null
            if (work.raagId == null) {
                val sid = work.startShabadId
                val eid = work.shabadIdEnd
                if (sid != null && eid != null) {
                    if (shabad.shabadId !in sid..eid) return@mapNotNull null
                } else {
                    if (ang.number !in work.angStart..work.angEnd) return@mapNotNull null
                }
            }
        }
        val shabadWork = meta?.raagId?.let { worksByRaag[it] }

        val lines = if (q.isBlank()) {
            shabad.lines
        } else {
            shabad.lines.filter { line ->
                line.gurmukhi.lowercase().contains(q) ||
                    line.roman.lowercase().contains(q) ||
                    line.sahibSinghRu.lowercase().contains(q) ||
                    line.sahibSinghPa.lowercase().contains(q)
            }
        }
        if (lines.isEmpty()) return@mapNotNull null

        VisibleShabad(
            shabad = shabad,
            raagName = meta?.raagId?.let { raags[it]?.nameRu } ?: "SGGS",
            authorName = meta?.authorId?.let { authors[it]?.nameRu } ?: "Автор не указан",
            workTitle = shabadWork?.titleRu,
            workSubtitle = shabadWork?.titleGurmukhi,
            showWorkHeader = false,
            lines = lines,
        )
    }

    return visible.mapIndexed { index, item ->
        val previous = visible.getOrNull(index - 1)
        item.copy(showWorkHeader = item.workTitle != null && item.workTitle != previous?.workTitle)
    }
}

fun selectionSubtitle(corpus: Corpus?, raagId: String?, authorId: String?, workId: String?): String {
    if (corpus == null) return ""
    return buildList {
        workId?.let { id -> corpus.works.firstOrNull { it.id == id }?.let { add("Произведение: ${it.titleRu}") } }
        raagId?.let { id -> corpus.raags.firstOrNull { it.id == id }?.let { add("Раздел: ${it.nameRu}") } }
        authorId?.let { id -> corpus.authors.firstOrNull { it.id == id }?.let { add("Автор: ${it.nameRu}") } }
    }.joinToString(" · ")
}

fun buildReaderTitle(currentRaag: Raag?, selectedAng: Int, contextSubtitle: String): String {
    val base = currentRaag?.let { "${it.nameRu} · ${it.nameGu}" } ?: "Анг $selectedAng"
    return if (contextSubtitle.isBlank()) base else "$base · $contextSubtitle"
}

fun searchScopeSummary(corpus: Corpus, raagId: String?, authorId: String?, workId: String?): String {
    return buildList {
        workId?.let { id -> corpus.works.firstOrNull { it.id == id }?.let { add("Произведение: ${it.titleRu}") } }
        raagId?.let { id -> corpus.raags.firstOrNull { it.id == id }?.let { add("Раздел: ${it.nameRu}") } }
        authorId?.let { id -> corpus.authors.firstOrNull { it.id == id }?.let { add("Автор: ${it.nameRu}") } }
    }.joinToString(" · ")
}

fun filterSearchResults(
    corpus: Corpus,
    shabadMeta: Map<Int, ShabadMeta>,
    results: List<SearchResult>,
    selectedRaagId: String?,
    selectedAuthorId: String?,
    selectedWorkId: String?,
): List<SearchResult> {
    if (selectedRaagId == null && selectedAuthorId == null && selectedWorkId == null) return results

    val work = selectedWorkId?.let { id -> corpus.works.firstOrNull { it.id == id } }
    return results.filter { result ->
        val meta = shabadMeta[result.shabadId]
        if (selectedRaagId != null && meta?.raagId != selectedRaagId) return@filter false
        if (selectedAuthorId != null && meta?.authorId != selectedAuthorId) return@filter false
        if (work != null) {
            if (work.raagId != null && meta?.raagId != work.raagId) return@filter false
            if (work.raagId == null) {
                val sid = work.startShabadId
                val eid = work.shabadIdEnd
                if (sid != null && eid != null) {
                    if (result.shabadId !in sid..eid) return@filter false
                } else {
                    if (result.ang !in work.angStart..work.angEnd) return@filter false
                }
            }
        }
        true
    }
}

fun angMatchesSelection(
    corpus: Corpus,
    angNumber: Int,
    selectedRaagId: String?,
    selectedAuthorId: String?,
    selectedWorkId: String?,
): Boolean {
    if (selectedRaagId == null && selectedAuthorId == null && selectedWorkId == null) return true

    val meta = corpus.shabads.filter { it.ang == angNumber }
    val work = selectedWorkId?.let { id -> corpus.works.firstOrNull { it.id == id } }
    return meta.any { item ->
        if (selectedRaagId != null && item.raagId != selectedRaagId) return@any false
        if (selectedAuthorId != null && item.authorId != selectedAuthorId) return@any false
        if (work != null) {
            if (work.raagId != null && item.raagId != work.raagId) return@any false
            if (work.raagId == null) {
                val sid = work.startShabadId
                val eid = work.shabadIdEnd
                if (sid != null && eid != null) {
                    if (item.shabadId !in sid..eid) return@any false
                } else {
                    if (angNumber !in work.angStart..work.angEnd) return@any false
                }
            }
        }
        true
    }
}

fun matchingAngNumbers(
    corpus: Corpus,
    selectedRaagId: String?,
    selectedAuthorId: String?,
    selectedWorkId: String?,
): List<Int> {
    return (corpus.manifest.angStart..corpus.manifest.angEnd).filter { angNumber ->
        angMatchesSelection(
            corpus = corpus,
            angNumber = angNumber,
            selectedRaagId = selectedRaagId,
            selectedAuthorId = selectedAuthorId,
            selectedWorkId = selectedWorkId,
        )
    }
}

fun previousFilteredAng(
    corpus: Corpus?,
    selectedAng: Int,
    selectedRaagId: String?,
    selectedAuthorId: String?,
    selectedWorkId: String?,
): Int? {
    if (corpus == null) return null
    val matching = matchingAngNumbers(corpus, selectedRaagId, selectedAuthorId, selectedWorkId)
    val index = matching.indexOf(selectedAng)
    return if (index > 0) matching[index - 1] else null
}

fun nextFilteredAng(
    corpus: Corpus?,
    selectedAng: Int,
    selectedRaagId: String?,
    selectedAuthorId: String?,
    selectedWorkId: String?,
): Int? {
    if (corpus == null) return null
    val matching = matchingAngNumbers(corpus, selectedRaagId, selectedAuthorId, selectedWorkId)
    val index = matching.indexOf(selectedAng)
    return if (index >= 0 && index < matching.lastIndex) matching[index + 1] else null
}

fun searchRussianText(context: Context, corpus: Corpus, query: String): List<SearchResult> {
    val q = normalizeSearchText(query)
    if (q.length < 2) return emptyList()

    val results = mutableListOf<SearchResult>()
    for (angNumber in corpus.manifest.angStart..corpus.manifest.angEnd) {
        val obj = JSONObject(context.readAsset("sggs_ru/angs/ksd_ang_%04d.json".format(angNumber)))
        val shabads = obj.getJSONArray("shabads")
        for (shabadIndex in 0 until shabads.length()) {
            val shabad = shabads.getJSONObject(shabadIndex)
            val shabadId = shabad.optInt("shabad_id")
            val lines = shabad.getJSONArray("lines")
            for (lineIndex in 0 until lines.length()) {
                val line = lines.getJSONObject(lineIndex)
                val text = line
                    .optJSONObject("translations")
                    ?.russianMain()
                    .orEmpty()
                if (text.isNotBlank() && normalizeSearchText(text).contains(q)) {
                    results += SearchResult(
                        ang = angNumber,
                        shabadId = shabadId,
                        verseId = line.optInt("verse_id"),
                        text = text,
                    )
                }
            }
        }
    }
    return results
}

fun normalizeSearchText(value: String): String =
    value.lowercase()
        .replace('ё', 'е')
        .replace(Regex("\\s+"), " ")
        .trim()

fun loadCorpus(context: Context): Corpus {
    val manifest = JSONObject(context.readAsset("sggs_ru/sggs_manifest.json"))
    return Corpus(
        manifest = Manifest(
            title = manifest.optString("title"),
            angStart = manifest.optInt("ang_start", 1),
            angEnd = manifest.optInt("ang_end", 1430),
            lineCount = manifest.optInt("line_count", 0),
        ),
        raags = context.readJsonArray("sggs_ru/indexes/raags.json").mapObjects { obj ->
            Raag(
                id = obj.optString("id"),
                order = obj.optInt("order"),
                nameRu = obj.optString("name_ru"),
                nameGu = obj.optString("name_gu"),
                type = obj.optString("type"),
                angStart = obj.optInt("ang_start"),
                angEnd = obj.optInt("ang_end"),
            )
        }.sortedBy { it.order },
        authors = context.readJsonArray("sggs_ru/indexes/authors.json").mapObjects { obj ->
            Author(
                id = obj.optString("id"),
                nameRu = obj.optString("name_ru"),
                nameGu = obj.optString("name_gu"),
                type = obj.optString("type"),
                mahalla = obj.optNullableInt("mahalla"),
                angStart = obj.optInt("ang_start"),
                angEnd = obj.optInt("ang_end"),
            )
        }.sortedWith(
            compareBy<Author> { if (it.type == "mahalla") 0 else 1 }
                .thenBy { it.mahalla ?: Int.MAX_VALUE }
                .thenBy { it.nameRu },
        ),
        works = context.readJsonArray("sggs_ru/indexes/works.json").mapObjects { obj ->
            Work(
                id = obj.optString("id"),
                titleRu = obj.optString("title_ru"),
                titleGurmukhi = obj.optString("title_gurmukhi"),
                raagId = obj.optNullableString("raag_id"),
                angStart = obj.optInt("ang_start"),
                angEnd = obj.optInt("ang_end"),
                startShabadId = obj.optNullableInt("start_shabad_id"),
                shabadIdEnd = obj.optNullableInt("shabad_id_end"),
                startVerseId = obj.optNullableInt("start_verse_id"),
            )
        }.sortedWith(compareBy<Work> { it.angStart }.thenBy { it.angEnd }.thenBy { it.titleRu }),
        shabads = context.readJsonArray("sggs_ru/indexes/shabads.json").mapObjects { obj ->
            ShabadMeta(
                shabadId = obj.optInt("shabad_id"),
                ang = obj.optInt("ang"),
                raagId = obj.optNullableString("raag_id"),
                authorId = obj.optNullableString("author_id"),
            )
        },
        about = context.readAsset("sggs_ru/articles/about_sahib_singh_ru.md"),
    )
}

fun loadAng(context: Context, ang: Int): Ang {
    val obj = JSONObject(context.readAsset("sggs_ru/angs/ksd_ang_%04d.json".format(ang)))
    val shabads = obj.getJSONArray("shabads").mapObjects { shabad ->
        Shabad(
            shabadId = shabad.optInt("shabad_id"),
            rahaoVerseId = shabad.optNullableInt("rahao_verse_id"),
            lines = shabad.getJSONArray("lines").mapObjects { line ->
                val translations = line.optJSONObject("translations") ?: JSONObject()
                Line(
                    verseId = line.optInt("verse_id"),
                    isRahao = line.optBoolean("is_rahao"),
                    gurmukhi = line.optString("gurmukhi"),
                    roman = line.optString("roman"),
                    sahibSinghPa = translations.optJSONObject("sahib_singh_pa")?.optString("main").orEmpty(),
                    sahibSinghRu = translations.russianMain(),
                )
            },
        )
    }
    return Ang(number = obj.optInt("ang"), shabads = shabads)
}

fun Context.readAsset(path: String): String =
    assets.open(path).bufferedReader(Charsets.UTF_8).use { it.readText() }

fun Context.readJsonArray(path: String): JSONArray = JSONArray(readAsset(path))

fun <T> JSONArray.mapObjects(block: (JSONObject) -> T): List<T> =
    (0 until length()).map { index -> block(getJSONObject(index)) }

fun JSONObject.optNullableString(name: String): String? =
    if (isNull(name)) null else optString(name).takeIf { it.isNotBlank() }

fun JSONObject.optNullableInt(name: String): Int? =
    if (isNull(name)) null else optInt(name)

fun JSONObject.russianMain(): String {
    val sahibSingh = optJSONObject("sahib_singh_ru")?.optString("main").orEmpty()
    if (sahibSingh.isNotBlank()) return sahibSingh
    return optJSONObject("ksd_ru")?.optString("main").orEmpty()
}
