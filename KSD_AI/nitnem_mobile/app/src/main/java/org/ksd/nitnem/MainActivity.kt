package org.ksd.nitnem

import android.content.Context
import android.graphics.BitmapFactory
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.ElevatedCard
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalDrawerSheet
import androidx.compose.material3.ModalNavigationDrawer
import androidx.compose.material3.NavigationDrawerItem
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.material3.lightColorScheme
import androidx.compose.material3.rememberDrawerState
import androidx.compose.material3.DrawerValue
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
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.SpanStyle
import androidx.compose.ui.text.buildAnnotatedString
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.launch
import org.json.JSONObject

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            KsdNitnemTheme {
                KsdNitnemApp()
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
    val Context = Color(0xFF0055AA)
    val Comment = Color(0xFF888888)
    val Artistic = Color(0xFF333366)
    val Rahao = Color(0xFF880044)
}

data class InfoBlock(
    val id: String,
    val title: String,
    val body: String,
)

data class ReaderLine(
    val id: String,
    val ang: Int,
    val lineNumber: Int,
    val workId: String,
    val workTitle: String,
    val workUnitTitle: String,
    val authorName: String,
    val gurmukhi: String,
    val roman: String,
    val translation: String,
    val artistic: String?,
    val context: String?,
    val comment: String?,
    val isRahao: Boolean,
)

data class WorkIndex(
    val id: String,
    val order: Int,
    val title: String,
    val gurmukhiTitle: String,
    val description: String,
)

data class NitnemContent(
    val title: String,
    val subtitle: String,
    val infoBlocks: List<InfoBlock>,
    val updatesMarkdown: String,
    val conceptMarkdown: String,
    val appInfoMarkdown: String,
    val dictionaryMarkdown: String,
    val works: List<WorkIndex>,
    val lines: List<ReaderLine>,
)

data class DisplaySettings(
    val showRoman: Boolean,
    val showTranslation: Boolean,
    val showArtistic: Boolean,
    val showContext: Boolean,
    val showComments: Boolean,
    val showAuthor: Boolean,
)

@Composable
fun KsdNitnemTheme(content: @Composable () -> Unit) {
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

@OptIn(ExperimentalLayoutApi::class)
@Composable
fun KsdNitnemApp() {
    val updatesPageId = "__updates__"
    val ekGranthPageId = "__ek_granth__"
    val appInfoPageId = "__app_info__"
    val dictionaryPageId = "__dictionary__"
    val context = LocalContext.current
    val contentResult = remember {
        runCatching { loadNitnemContent(context) }
    }
    val content = contentResult.getOrNull()

    var selectedAng by rememberSaveable { mutableIntStateOf(1) }
    var settings by remember {
        mutableStateOf(
            DisplaySettings(
                showRoman = true,
                showTranslation = true,
                showArtistic = true,
                showContext = true,
                showComments = false,
                showAuthor = false,
            )
        )
    }
    var infoBlockId by rememberSaveable { mutableStateOf<String?>(null) }
    var selectedWorkId by rememberSaveable { mutableStateOf<String?>(null) }
    val drawerState = rememberDrawerState(DrawerValue.Closed)
    val listState = rememberLazyListState()
    val scope = rememberCoroutineScope()

    LaunchedEffect(selectedWorkId, selectedAng, infoBlockId) {
        val targetIndex = if (infoBlockId == null && selectedWorkId != null) 1 else 0
        listState.scrollToItem(targetIndex)
    }

    ModalNavigationDrawer(
        drawerState = drawerState,
        drawerContent = {
            ModalDrawerSheet(
                modifier = Modifier.width(312.dp),
                drawerContainerColor = ReaderColors.Surface,
            ) {
                LazyColumn(modifier = Modifier.fillMaxSize()) {
                    item {
                        Text(
                            text = "Nitnem Authentic",
                            modifier = Modifier.padding(20.dp, 20.dp, 20.dp, 8.dp),
                            color = ReaderColors.Ink,
                            fontWeight = FontWeight.SemiBold,
                            fontSize = 20.sp,
                        )
                        Text(
                            text = "Первые 13 ангов СГГС",
                            modifier = Modifier.padding(horizontal = 20.dp),
                            color = ReaderColors.Muted,
                            fontSize = 14.sp,
                        )
                        Spacer(Modifier.height(12.dp))
                        Text(
                            text = "Произведения",
                            modifier = Modifier.padding(horizontal = 20.dp, vertical = 8.dp),
                            color = ReaderColors.Muted,
                            fontSize = 13.sp,
                            fontWeight = FontWeight.SemiBold,
                        )
                    }
                    items(content?.works.orEmpty(), key = { it.id }) { work ->
                        NavigationDrawerItem(
                            label = {
                                Column {
                                    Text(work.title)
                                    if (work.gurmukhiTitle.isNotBlank()) {
                                        Text(
                                            text = work.gurmukhiTitle,
                                            color = ReaderColors.Gurmukhi,
                                            fontSize = 13.sp,
                                        )
                                    }
                                }
                            },
                            selected = infoBlockId == null && selectedWorkId == work.id,
                            onClick = {
                                infoBlockId = null
                                selectedWorkId = work.id
                                val firstAng = content?.lines?.firstOrNull { it.workId == work.id }?.ang
                                if (firstAng != null) selectedAng = firstAng
                                scope.launch { drawerState.close() }
                            },
                            modifier = Modifier.padding(horizontal = 12.dp),
                        )
                    }
                    item {
                        Spacer(Modifier.height(12.dp))
                        Text(
                            text = "Информация",
                            modifier = Modifier.padding(horizontal = 20.dp, vertical = 8.dp),
                            color = ReaderColors.Muted,
                            fontSize = 13.sp,
                            fontWeight = FontWeight.SemiBold,
                        )
                    }
                    items(content?.infoBlocks.orEmpty(), key = { it.id }) { block ->
                        NavigationDrawerItem(
                            label = { Text(block.title) },
                            selected = infoBlockId == block.id,
                            onClick = {
                                infoBlockId = block.id
                                scope.launch { drawerState.close() }
                            },
                            modifier = Modifier.padding(horizontal = 12.dp),
                        )
                    }
                    item {
                        NavigationDrawerItem(
                            label = { Text("Обновления") },
                            selected = infoBlockId == updatesPageId,
                            onClick = {
                                infoBlockId = updatesPageId
                                scope.launch { drawerState.close() }
                            },
                            modifier = Modifier.padding(horizontal = 12.dp),
                        )
                        NavigationDrawerItem(
                            label = { Text("Ek Granth Ek Panth Ek Maryada") },
                            selected = infoBlockId == ekGranthPageId,
                            onClick = {
                                infoBlockId = ekGranthPageId
                                scope.launch { drawerState.close() }
                            },
                            modifier = Modifier.padding(horizontal = 12.dp),
                        )
                        NavigationDrawerItem(
                            label = { Text("Символ приложения") },
                            selected = infoBlockId == appInfoPageId,
                            onClick = {
                                infoBlockId = appInfoPageId
                                scope.launch { drawerState.close() }
                            },
                            modifier = Modifier.padding(horizontal = 12.dp),
                        )
                        NavigationDrawerItem(
                            label = { Text("Словарь") },
                            selected = infoBlockId == dictionaryPageId,
                            onClick = {
                                infoBlockId = dictionaryPageId
                                scope.launch { drawerState.close() }
                            },
                            modifier = Modifier.padding(horizontal = 12.dp),
                        )
                        Spacer(Modifier.height(12.dp))
                        Text(
                            text = "Анги",
                            modifier = Modifier.padding(horizontal = 20.dp, vertical = 8.dp),
                            color = ReaderColors.Muted,
                            fontSize = 13.sp,
                            fontWeight = FontWeight.SemiBold,
                        )
                    }
                    items(content?.lines.orEmpty().map { it.ang }.distinct()) { ang ->
                        NavigationDrawerItem(
                            label = { Text("Анг $ang") },
                            selected = infoBlockId == null && selectedWorkId == null && selectedAng == ang,
                            onClick = {
                                infoBlockId = null
                                selectedWorkId = null
                                selectedAng = ang
                                scope.launch { drawerState.close() }
                            },
                            modifier = Modifier.padding(horizontal = 12.dp),
                        )
                    }
                }
            }
        },
    ) {
        Scaffold(
            containerColor = ReaderColors.Page,
            topBar = {
                ReaderTopBar(
                    title = content?.title ?: "Nitnem Authentic",
                    selectedAng = selectedAng,
                    selectedWorkTitle = content?.works?.firstOrNull { it.id == selectedWorkId }?.title,
                    onMenuClick = { scope.launch { drawerState.open() } },
                    onPreviousAng = {
                        if (selectedAng > 1) {
                            selectedAng -= 1
                            selectedWorkId = null
                            infoBlockId = null
                            scope.launch { listState.scrollToItem(0) }
                        }
                    },
                    onNextAng = {
                        if (selectedAng < 13) {
                            selectedAng += 1
                            selectedWorkId = null
                            infoBlockId = null
                            scope.launch { listState.scrollToItem(0) }
                        }
                    },
                )
            },
        ) { padding ->
            if (content == null) {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(padding),
                    contentAlignment = Alignment.Center,
                ) {
                    Text(
                        text = contentResult.exceptionOrNull()?.message ?: "Не удалось открыть JSON",
                        color = ReaderColors.Rahao,
                    )
                }
            } else {
                LazyColumn(
                    state = listState,
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(padding),
                    contentPadding = PaddingValues(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp),
                ) {
                    item {
                        SettingsPanel(settings = settings, onChange = { settings = it })
                    }

                    when {
                        infoBlockId == updatesPageId -> {
                            item {
                                MarkdownCard(markdown = content.updatesMarkdown)
                            }
                        }
                        infoBlockId == ekGranthPageId -> {
                            item {
                                MarkdownImageCard(
                                    markdown = content.conceptMarkdown,
                                    imagePaths = listOf("images/ek_granth_ek_panth.webp"),
                                )
                            }
                        }
                        infoBlockId == appInfoPageId -> {
                            item {
                                MarkdownImageCard(
                                    markdown = content.appInfoMarkdown,
                                    imagePaths = listOf("images/logo_of_app.jpg"),
                                )
                            }
                        }
                        infoBlockId == dictionaryPageId -> {
                            item {
                                MarkdownCard(markdown = content.dictionaryMarkdown)
                            }
                        }
                        content.infoBlocks.any { it.id == infoBlockId } -> {
                            item {
                                InfoBlockCard(
                                    block = content.infoBlocks.first { it.id == infoBlockId },
                                )
                            }
                        }
                        else -> {
                            val visibleLines = if (selectedWorkId != null) {
                                content.lines.filter { it.workId == selectedWorkId }
                            } else {
                                content.lines.filter { it.ang == selectedAng }
                            }
                            items(
                                items = visibleLines,
                                key = { it.id },
                            ) { line ->
                                LineCard(line = line, settings = settings)
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun MarkdownCard(markdown: String) {
    ElevatedCard(
        colors = CardDefaults.elevatedCardColors(containerColor = ReaderColors.Surface),
        shape = RoundedCornerShape(8.dp),
    ) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            MarkdownBody(markdown = markdown)
        }
    }
}

@Composable
fun MarkdownImageCard(markdown: String, imagePaths: List<String>) {
    ElevatedCard(
        colors = CardDefaults.elevatedCardColors(containerColor = ReaderColors.Surface),
        shape = RoundedCornerShape(8.dp),
    ) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
            imagePaths.forEach { assetPath ->
                AssetImage(
                    assetPath = assetPath,
                    modifier = Modifier.fillMaxWidth(),
                )
            }
            MarkdownBody(markdown = markdown)
        }
    }
}

@Composable
fun MarkdownBody(markdown: String) {
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        markdown.lines().forEach { rawLine ->
            val line = rawLine.trim()
            when {
                line.isBlank() -> Spacer(Modifier.height(4.dp))
                line.startsWith("# ") -> Text(
                    text = line.removePrefix("# "),
                    color = ReaderColors.Ink,
                    fontWeight = FontWeight.SemiBold,
                    fontSize = 22.sp,
                )
                line.startsWith("## ") -> Text(
                    text = line.removePrefix("## "),
                    color = ReaderColors.Context,
                    fontWeight = FontWeight.SemiBold,
                    fontSize = 17.sp,
                )
                line.startsWith("- ") -> Text(
                    text = "• ${line.removePrefix("- ")}",
                    color = ReaderColors.Ink,
                    fontSize = 15.sp,
                    lineHeight = 22.sp,
                )
                line.startsWith("[g] ") -> Text(
                    text = line.removePrefix("[g] "),
                    color = ReaderColors.Gurmukhi,
                    fontSize = 21.sp,
                    lineHeight = 29.sp,
                    fontWeight = FontWeight.Medium,
                )
                line.startsWith("[r] ") -> Text(
                    text = line.removePrefix("[r] "),
                    color = ReaderColors.Roman,
                    fontSize = 14.sp,
                    lineHeight = 20.sp,
                )
                line.startsWith("[t] ") -> Text(
                    text = line.removePrefix("[t] "),
                    color = ReaderColors.Translation,
                    fontSize = 16.sp,
                    lineHeight = 23.sp,
                )
                line.startsWith("[ref] ") -> Text(
                    text = line.removePrefix("[ref] "),
                    color = ReaderColors.Context,
                    fontSize = 13.sp,
                    lineHeight = 19.sp,
                )
                else -> Text(
                    text = line,
                    color = ReaderColors.Ink,
                    fontSize = 15.sp,
                    lineHeight = 22.sp,
                )
            }
        }
    }
}

@Composable
fun AssetImage(assetPath: String, modifier: Modifier = Modifier) {
    val context = LocalContext.current
    val bitmap = remember(assetPath) {
        runCatching {
            context.assets.open(assetPath).use { BitmapFactory.decodeStream(it) }
        }.getOrNull()
    }
    if (bitmap != null) {
        Image(
            bitmap = bitmap.asImageBitmap(),
            contentDescription = null,
            modifier = modifier,
            contentScale = ContentScale.FillWidth,
        )
    }
}

@Composable
fun ReaderTopBar(
    title: String,
    selectedAng: Int,
    selectedWorkTitle: String?,
    onMenuClick: () -> Unit,
    onPreviousAng: () -> Unit,
    onNextAng: () -> Unit,
) {
    Surface(
        color = ReaderColors.Surface,
        shadowElevation = 1.dp,
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp, 12.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween,
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = title,
                    color = ReaderColors.Ink,
                    fontWeight = FontWeight.SemiBold,
                    fontSize = 20.sp,
                )
                Row(verticalAlignment = Alignment.CenterVertically) {
                    IconButton(
                        onClick = onPreviousAng,
                        enabled = selectedAng > 1,
                    ) {
                        Text("‹", color = ReaderColors.Ink, fontSize = 24.sp)
                    }
                    OutlinedButton(
                        onClick = onMenuClick,
                        colors = ButtonDefaults.outlinedButtonColors(contentColor = ReaderColors.Ink),
                        border = BorderStroke(1.dp, ReaderColors.Border),
                    ) {
                        Text(selectedWorkTitle ?: "Анг $selectedAng")
                    }
                    IconButton(
                        onClick = onNextAng,
                        enabled = selectedAng < 13,
                    ) {
                        Text("›", color = ReaderColors.Ink, fontSize = 24.sp)
                    }
                }
            }
            OutlinedButton(
                onClick = onMenuClick,
                colors = ButtonDefaults.outlinedButtonColors(contentColor = ReaderColors.Ink),
                border = BorderStroke(1.dp, ReaderColors.Border),
            ) {
                Text("Меню")
            }
        }
    }
}

@Composable
fun ReaderChip(text: String, onClick: () -> Unit) {
    OutlinedButton(
        onClick = onClick,
        shape = RoundedCornerShape(8.dp),
        border = BorderStroke(1.dp, ReaderColors.Border),
        colors = ButtonDefaults.outlinedButtonColors(contentColor = ReaderColors.Ink),
    ) {
        Text(text)
    }
}

@Composable
fun SettingsPanel(settings: DisplaySettings, onChange: (DisplaySettings) -> Unit) {
    ElevatedCard(
        colors = CardDefaults.elevatedCardColors(containerColor = ReaderColors.Surface),
        shape = RoundedCornerShape(8.dp),
    ) {
        Column(Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(2.dp)) {
            Text(
                text = "Вид текста",
                color = ReaderColors.Ink,
                fontWeight = FontWeight.SemiBold,
                fontSize = 15.sp,
            )
            SettingRow("Транслитерация", settings.showRoman) {
                onChange(settings.copy(showRoman = it))
            }
            SettingRow("Основной перевод", settings.showTranslation) {
                onChange(settings.copy(showTranslation = it))
            }
            SettingRow("Художественный слой", settings.showArtistic) {
                onChange(settings.copy(showArtistic = it))
            }
            SettingRow("Контекст", settings.showContext) {
                onChange(settings.copy(showContext = it))
            }
            SettingRow("Обоснование перевода", settings.showComments) {
                onChange(settings.copy(showComments = it))
            }
            SettingRow("Автор", settings.showAuthor) {
                onChange(settings.copy(showAuthor = it))
            }
        }
    }
}

@Composable
fun SettingRow(label: String, checked: Boolean, onCheckedChange: (Boolean) -> Unit) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .height(46.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.SpaceBetween,
    ) {
        Text(text = label, color = ReaderColors.Ink, fontSize = 15.sp)
        Switch(checked = checked, onCheckedChange = onCheckedChange)
    }
}

@Composable
fun InfoBlockCard(block: InfoBlock) {
    ElevatedCard(
        colors = CardDefaults.elevatedCardColors(containerColor = ReaderColors.Surface),
        shape = RoundedCornerShape(8.dp),
    ) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Text(
                text = block.title,
                color = ReaderColors.Ink,
                fontWeight = FontWeight.SemiBold,
                fontSize = 20.sp,
            )
            MarkdownBody(markdown = block.body)
        }
    }
}

@Composable
fun LineCard(line: ReaderLine, settings: DisplaySettings) {
    var expanded by rememberSaveable(line.id) { mutableStateOf(true) }
    val borderColor = if (line.isRahao) ReaderColors.Rahao else ReaderColors.Border

    Card(
        colors = CardDefaults.elevatedCardColors(containerColor = ReaderColors.Surface),
        shape = RoundedCornerShape(8.dp),
        border = BorderStroke(1.dp, borderColor.copy(alpha = 0.55f)),
    ) {
        Column(Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(7.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text(
                    text = "${line.workTitle} · ${line.workUnitTitle} · Анг ${line.ang} · строка ${line.lineNumber}",
                    color = if (line.isRahao) ReaderColors.Rahao else ReaderColors.Muted,
                    fontSize = 12.sp,
                    fontWeight = FontWeight.SemiBold,
                )
                IconButton(onClick = { expanded = !expanded }) {
                    Text(
                        text = if (expanded) "⌃" else "⌄",
                        color = ReaderColors.Muted,
                        fontSize = 22.sp,
                        fontWeight = FontWeight.SemiBold,
                    )
                }
            }
            Text(
                text = line.gurmukhi,
                color = if (line.isRahao) ReaderColors.Rahao else ReaderColors.Gurmukhi,
                fontSize = 22.sp,
                lineHeight = 30.sp,
                fontWeight = FontWeight.Medium,
            )
            AnimatedVisibility(visible = expanded) {
                Column(verticalArrangement = Arrangement.spacedBy(7.dp)) {
                    if (settings.showRoman && line.roman.isNotBlank()) {
                        Text(text = line.roman, color = ReaderColors.Roman, fontSize = 14.sp)
                    }
                    if (settings.showAuthor && line.authorName.isNotBlank()) {
                        Text(
                            text = line.authorName,
                            color = ReaderColors.Muted,
                            fontSize = 13.sp,
                        )
                    }
                    if (settings.showTranslation && line.translation.isNotBlank()) {
                        Text(
                            text = buildTranslationText(line.translation),
                            color = ReaderColors.Translation,
                            fontSize = 17.sp,
                            lineHeight = 24.sp,
                        )
                    }
                    if (settings.showArtistic && !line.artistic.isNullOrBlank()) {
                        Text(
                            text = "〜 ${line.artistic}",
                            color = ReaderColors.Artistic,
                            fontSize = 16.sp,
                            lineHeight = 23.sp,
                        )
                    }
                    if (settings.showContext && !line.context.isNullOrBlank()) {
                        Text(
                            text = line.context,
                            color = ReaderColors.Context,
                            fontSize = 14.sp,
                            lineHeight = 20.sp,
                        )
                    }
                    if (settings.showComments && !line.comment.isNullOrBlank()) {
                        Text(
                            text = line.comment,
                            color = ReaderColors.Comment,
                            fontSize = 14.sp,
                            lineHeight = 20.sp,
                        )
                    }
                }
            }
        }
    }
}

fun buildTranslationText(text: String) = buildAnnotatedString {
    var index = 0
    while (index < text.length) {
        val start = text.indexOf("[[", startIndex = index)
        if (start == -1) {
            append(text.substring(index))
            break
        }

        append(text.substring(index, start))
        val end = text.indexOf("]]", startIndex = start + 2)
        if (end == -1) {
            append(text.substring(start))
            break
        }

        pushStyle(SpanStyle(color = ReaderColors.Context))
        append(text.substring(start + 2, end))
        pop()
        index = end + 2
    }
}

fun loadNitnemContent(context: Context): NitnemContent {
    val text = context.assets.open("nitnem_ru_ksd_v1.json")
        .bufferedReader(Charsets.UTF_8)
        .use { it.readText() }
    val root = JSONObject(text)
    val bani = root.getJSONArray("banis").getJSONObject(0)
    val works = root.optJSONArray("works").toObjectList { work ->
        WorkIndex(
            id = work.optString("id"),
            order = work.optInt("order"),
            title = work.optString("title_ru"),
            gurmukhiTitle = work.optString("title_gurmukhi"),
            description = work.optString("description_ru"),
        )
    }.sortedBy { it.order }
    val infoBlocks = bani.optJSONArray("info_blocks").toObjectList { block ->
        InfoBlock(
            id = block.optString("id"),
            title = block.optString("title"),
            body = block.optString("body"),
        )
    }.filterNot {
        it.id in setOf("ek_granth_ek_panth", "why_first_13_angs", "sggs_basis")
    }

    val lines = mutableListOf<ReaderLine>()
    val angs = root.getJSONArray("angs")
    for (angIndex in 0 until angs.length()) {
        val ang = angs.getJSONObject(angIndex)
        val angNumber = ang.optInt("ang")
        val shabads = ang.getJSONArray("shabads")
        for (shabadIndex in 0 until shabads.length()) {
            val shabad = shabads.getJSONObject(shabadIndex)
            val shabadLines = shabad.getJSONArray("lines")
            for (lineIndex in 0 until shabadLines.length()) {
                val line = shabadLines.getJSONObject(lineIndex)
                val translation = line.optJSONObject("translations")
                    ?.optJSONObject("ksd_ru")
                    ?: JSONObject()
                lines += ReaderLine(
                    id = line.optString("id", "ang-$angNumber-$shabadIndex-$lineIndex"),
                    ang = angNumber,
                    lineNumber = line.optInt("verse_id", lineIndex + 1),
                    workId = line.optString("work_id"),
                    workTitle = line.optString("work_title_ru"),
                    workUnitTitle = line.optString("work_unit_title_ru"),
                    authorName = line.optString("author_name_ru"),
                    gurmukhi = line.optString("gurmukhi"),
                    roman = line.optString("roman_display", line.optString("roman")),
                    translation = translation.optString("main"),
                    artistic = translation.optNullableString("artistic"),
                    context = translation.optNullableString("context_note"),
                    comment = translation.optNullableString("confidence_reason"),
                    isRahao = line.optBoolean("is_rahao"),
                )
            }
        }
    }

    return NitnemContent(
        title = bani.optString("title", "Nitnem Authentic"),
        subtitle = bani.optString("subtitle", "Первые 13 ангов СГГС"),
        infoBlocks = infoBlocks,
        updatesMarkdown = context.loadAssetTextOrBlank("updates.md"),
        conceptMarkdown = context.loadAssetTextOrBlank("ek_granth_maryada.md"),
        appInfoMarkdown = context.loadAssetTextOrBlank("app_info.md"),
        dictionaryMarkdown = context.loadAssetTextOrBlank("dictionary.md"),
        works = works,
        lines = lines,
    )
}

private fun Context.loadAssetTextOrBlank(name: String): String =
    runCatching {
        assets.open(name)
            .bufferedReader(Charsets.UTF_8)
            .use { it.readText() }
    }.getOrDefault("")

private inline fun <T> org.json.JSONArray?.toObjectList(
    crossinline mapper: (JSONObject) -> T,
): List<T> {
    if (this == null) return emptyList()
    return buildList {
        for (index in 0 until length()) {
            add(mapper(getJSONObject(index)))
        }
    }
}

private fun JSONObject.optNullableString(name: String): String? {
    val value = optString(name)
    return value.takeIf { it.isNotBlank() }
}
