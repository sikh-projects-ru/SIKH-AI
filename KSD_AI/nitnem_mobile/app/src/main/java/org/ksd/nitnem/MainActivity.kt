package org.ksd.nitnem

import android.content.Context
import android.graphics.BitmapFactory
import android.net.Uri
import android.os.Bundle
import android.text.Html
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Image
import androidx.compose.foundation.clickable
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
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.buildAnnotatedString
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import kotlinx.coroutines.Dispatchers
import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.net.URL
import java.security.MessageDigest

private const val NITNEM_PACKAGE_ID = "nitnem_ru_sikhizm_resolved"
private const val NITNEM_CONTENT_FILE = "nitnem_ru_ksd_v1.json"
private val NITNEM_API_BASES = listOf(
    "https://sikhizm.ru/wp-json/ksd-nitnem/v1",
    "http://sikhizm.ru/wp-json/ksd-nitnem/v1",
)

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
    val ExplanationText = Color(0xFF5C4B00)
    val ExplanationBg = Color(0xFFFFF9DF)
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
    val packageId: String,
    val schemaVersion: Int,
    val contentVersion: Int,
    val generatedAt: String,
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

data class ContentSyncStatus(
    val message: String,
    val isChecking: Boolean = false,
    val canRetry: Boolean = false,
)

private sealed interface ContentSyncResult {
    data object UpToDate : ContentSyncResult
    data class Updated(val contentVersion: Int, val diffs: List<LineDiff> = emptyList()) : ContentSyncResult
    data class Skipped(val reason: String) : ContentSyncResult
}

data class FieldDiff(val label: String, val old: String, val new: String)

data class LineDiff(
    val lineId: String,
    val ang: Int,
    val workId: String,
    val workTitle: String,
    val gurmukhi: String,
    val changedFields: List<FieldDiff>,
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
    val changesPageId = "__changes__"
    val context = LocalContext.current
    var contentResult by remember {
        mutableStateOf(runCatching { loadNitnemContent(context) })
    }
    val content = contentResult.getOrNull()
    val availableAngs = remember(content) {
        content?.lines?.map { it.ang }?.distinct()?.sorted() ?: emptyList()
    }
    var syncStatus by remember {
        mutableStateOf(ContentSyncStatus("Проверка обновлений ещё не запускалась"))
    }
    var showUpdateNotice by remember { mutableStateOf(false) }
    var syncTrigger by remember { mutableIntStateOf(0) }
    var contentDiffs by remember { mutableStateOf(loadContentDiff(context)) }

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
    val worksOrdered = remember(content) { content?.works?.sortedBy { it.order } ?: emptyList() }

    LaunchedEffect(selectedWorkId, selectedAng, infoBlockId) {
        val targetIndex = if (infoBlockId == null && selectedWorkId != null) 1 else 0
        listState.scrollToItem(targetIndex)
    }

    LaunchedEffect(syncTrigger) {
        val localVersion = contentResult.getOrNull()?.contentVersion ?: 0
        syncStatus = ContentSyncStatus("Проверяем обновления текста", isChecking = true)
        val result = withContext(Dispatchers.IO) {
            checkAndUpdateNitnemContent(context, localVersion)
        }
        syncStatus = when (result) {
            ContentSyncResult.UpToDate -> ContentSyncStatus("Текст обновлён до последней версии")
            is ContentSyncResult.Updated -> {
                contentResult = runCatching { loadNitnemContent(context) }
                if (result.diffs.isNotEmpty()) contentDiffs = result.diffs
                showUpdateNotice = true
                ContentSyncStatus("Загружена новая версия текста: ${result.contentVersion}")
            }
            is ContentSyncResult.Skipped -> ContentSyncStatus(result.reason, canRetry = true)
        }
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
                            text = "Нитнем",
                            modifier = Modifier.padding(horizontal = 20.dp, vertical = 8.dp),
                            color = ReaderColors.Muted,
                            fontSize = 13.sp,
                            fontWeight = FontWeight.SemiBold,
                        )
                    }
                    val nitnemWorkIds = setOf("jap", "so_dar", "so_purakh", "sohila")
                    items(
                        content?.works.orEmpty().filter { it.id in nitnemWorkIds },
                        key = { it.id },
                    ) { work ->
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
                    val otherBaniWorks = content?.works.orEmpty().filterNot { it.id in nitnemWorkIds }
                    if (otherBaniWorks.isNotEmpty()) {
                        item {
                            Text(
                                text = "Другие Бани",
                                modifier = Modifier.padding(horizontal = 20.dp, vertical = 8.dp),
                                color = ReaderColors.Muted,
                                fontSize = 13.sp,
                                fontWeight = FontWeight.SemiBold,
                            )
                        }
                        items(otherBaniWorks, key = { it.id }) { work ->
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
                        if (contentDiffs.isNotEmpty()) {
                            NavigationDrawerItem(
                                label = { Text("Что изменилось") },
                                selected = infoBlockId == changesPageId,
                                onClick = {
                                    infoBlockId = changesPageId
                                    scope.launch { drawerState.close() }
                                },
                                modifier = Modifier.padding(horizontal = 12.dp),
                            )
                        }
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
                val angIdx = availableAngs.indexOf(selectedAng)
                val workIdx = worksOrdered.indexOfFirst { it.id == selectedWorkId }
                ReaderTopBar(
                    title = content?.title ?: "Nitnem Authentic",
                    selectedAng = selectedAng,
                    selectedWorkTitle = content?.works?.firstOrNull { it.id == selectedWorkId }?.title,
                    showNavigation = infoBlockId == null,
                    canGoBack = infoBlockId == null && (
                        (selectedWorkId == null && angIdx > 0) ||
                        (selectedWorkId != null && workIdx > 0)
                    ),
                    canGoForward = infoBlockId == null && (
                        (selectedWorkId == null && angIdx in 0 until availableAngs.lastIndex) ||
                        (selectedWorkId != null && workIdx in 0 until worksOrdered.lastIndex)
                    ),
                    onMenuClick = { scope.launch { drawerState.open() } },
                    onPreviousAng = {
                        if (selectedWorkId != null && workIdx > 0) {
                            val prev = worksOrdered[workIdx - 1]
                            selectedWorkId = prev.id
                            content?.lines?.firstOrNull { it.workId == prev.id }?.ang?.let { selectedAng = it }
                            scope.launch { listState.scrollToItem(0) }
                        } else if (selectedWorkId == null) {
                            val idx = availableAngs.indexOf(selectedAng)
                            if (idx > 0) {
                                selectedAng = availableAngs[idx - 1]
                                infoBlockId = null
                                scope.launch { listState.scrollToItem(0) }
                            }
                        }
                    },
                    onNextAng = {
                        if (selectedWorkId != null && workIdx in 0 until worksOrdered.lastIndex) {
                            val next = worksOrdered[workIdx + 1]
                            selectedWorkId = next.id
                            content?.lines?.firstOrNull { it.workId == next.id }?.ang?.let { selectedAng = it }
                            scope.launch { listState.scrollToItem(0) }
                        } else if (selectedWorkId == null) {
                            val idx = availableAngs.indexOf(selectedAng)
                            if (idx in 0 until availableAngs.lastIndex) {
                                selectedAng = availableAngs[idx + 1]
                                infoBlockId = null
                                scope.launch { listState.scrollToItem(0) }
                            }
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
                        SettingsPanel(
                            settings = settings,
                            contentVersion = content.contentVersion,
                            syncStatus = syncStatus,
                            onChange = { settings = it },
                            onRetry = { syncTrigger++ },
                        )
                    }
                    if (showUpdateNotice) {
                        item {
                            UpdateNoticeBanner(
                                onViewUpdates = {
                                    showUpdateNotice = false
                                    infoBlockId = if (contentDiffs.isNotEmpty()) changesPageId else updatesPageId
                                },
                                onDismiss = { showUpdateNotice = false },
                            )
                        }
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
                        infoBlockId == changesPageId -> {
                            item {
                                ElevatedCard(
                                    colors = CardDefaults.elevatedCardColors(containerColor = ReaderColors.Surface),
                                    shape = RoundedCornerShape(8.dp),
                                ) {
                                    Column(
                                        Modifier.padding(16.dp),
                                        verticalArrangement = Arrangement.spacedBy(4.dp),
                                    ) {
                                        Text(
                                            text = "Что изменилось",
                                            color = ReaderColors.Ink,
                                            fontWeight = FontWeight.SemiBold,
                                            fontSize = 20.sp,
                                        )
                                        Text(
                                            text = if (contentDiffs.isEmpty()) "Нет сохранённых изменений"
                                                   else "${contentDiffs.size} строк обновлено",
                                            color = ReaderColors.Muted,
                                            fontSize = 14.sp,
                                        )
                                    }
                                }
                            }
                            items(contentDiffs, key = { it.lineId }) { diff ->
                                LineDiffCard(diff)
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
                                LineCard(
                                    line = line,
                                    settings = settings,
                                    allLines = content.lines,
                                    works = content.works,
                                    onOpenReference = { target ->
                                        infoBlockId = null
                                        selectedWorkId = null
                                        selectedAng = target.ang
                                        scope.launch {
                                            val targetIndex = content.lines
                                                .filter { it.ang == target.ang }
                                                .indexOfFirst { it.id == target.id }
                                                .coerceAtLeast(0)
                                            listState.scrollToItem(targetIndex + 1)
                                        }
                                    },
                                    onOpenWork = { workId ->
                                        infoBlockId = null
                                        selectedWorkId = workId
                                        val firstAng = content.lines.firstOrNull { it.workId == workId }?.ang
                                        if (firstAng != null) selectedAng = firstAng
                                        scope.launch { listState.scrollToItem(0) }
                                    },
                                )
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
    showNavigation: Boolean = true,
    canGoBack: Boolean,
    canGoForward: Boolean,
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
                    if (showNavigation) {
                        IconButton(onClick = onPreviousAng, enabled = canGoBack) {
                            Text("‹", color = ReaderColors.Ink, fontSize = 24.sp)
                        }
                    }
                    OutlinedButton(
                        onClick = onMenuClick,
                        colors = ButtonDefaults.outlinedButtonColors(contentColor = ReaderColors.Ink),
                        border = BorderStroke(1.dp, ReaderColors.Border),
                    ) {
                        Text(selectedWorkTitle ?: "Анг $selectedAng")
                    }
                    if (showNavigation) {
                        IconButton(onClick = onNextAng, enabled = canGoForward) {
                            Text("›", color = ReaderColors.Ink, fontSize = 24.sp)
                        }
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
fun UpdateNoticeBanner(onViewUpdates: () -> Unit, onDismiss: () -> Unit) {
    ElevatedCard(
        colors = CardDefaults.elevatedCardColors(containerColor = Color(0xFFE8F5E9)),
        shape = RoundedCornerShape(8.dp),
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(14.dp, 12.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween,
        ) {
            Text(
                text = "Текст обновлён",
                color = Color(0xFF2E7D32),
                fontWeight = FontWeight.SemiBold,
                fontSize = 14.sp,
                modifier = Modifier.weight(1f),
            )
            OutlinedButton(
                onClick = onViewUpdates,
                colors = ButtonDefaults.outlinedButtonColors(contentColor = Color(0xFF2E7D32)),
                border = BorderStroke(1.dp, Color(0xFF81C784)),
                contentPadding = PaddingValues(horizontal = 12.dp, vertical = 4.dp),
            ) {
                Text("Обновления", fontSize = 13.sp)
            }
            IconButton(onClick = onDismiss) {
                Text("×", color = Color(0xFF2E7D32), fontSize = 20.sp, fontWeight = FontWeight.Bold)
            }
        }
    }
}

@Composable
fun LineDiffCard(diff: LineDiff) {
    ElevatedCard(
        colors = CardDefaults.elevatedCardColors(containerColor = ReaderColors.Surface),
        shape = RoundedCornerShape(8.dp),
    ) {
        Column(Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(
                text = "${diff.workTitle} · Анг ${diff.ang}",
                color = ReaderColors.Muted,
                fontSize = 12.sp,
                fontWeight = FontWeight.SemiBold,
            )
            Text(
                text = diff.gurmukhi,
                color = ReaderColors.Gurmukhi,
                fontSize = 18.sp,
                lineHeight = 26.sp,
                fontWeight = FontWeight.Medium,
            )
            diff.changedFields.forEach { field ->
                Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    FieldLabel(field.label)
                    if (field.old.isNotBlank()) {
                        Surface(color = Color(0xFFFFF3F3), shape = RoundedCornerShape(4.dp)) {
                            Row(
                                modifier = Modifier.fillMaxWidth().padding(8.dp, 6.dp),
                                horizontalArrangement = Arrangement.spacedBy(6.dp),
                            ) {
                                Text(
                                    text = "было",
                                    color = Color(0xFFB03030),
                                    fontSize = 10.sp,
                                    fontWeight = FontWeight.SemiBold,
                                    modifier = Modifier.width(36.dp),
                                )
                                Text(
                                    text = stripRichText(field.old),
                                    color = Color(0xFF994444),
                                    fontSize = 14.sp,
                                    lineHeight = 20.sp,
                                    modifier = Modifier.weight(1f),
                                )
                            }
                        }
                    }
                    Surface(color = Color(0xFFF0FFF3), shape = RoundedCornerShape(4.dp)) {
                        Row(
                            modifier = Modifier.fillMaxWidth().padding(8.dp, 6.dp),
                            horizontalArrangement = Arrangement.spacedBy(6.dp),
                        ) {
                            Text(
                                text = "стало",
                                color = Color(0xFF2E7D32),
                                fontSize = 10.sp,
                                fontWeight = FontWeight.SemiBold,
                                modifier = Modifier.width(36.dp),
                            )
                            Text(
                                text = stripRichText(field.new),
                                color = Color(0xFF1A4A1A),
                                fontSize = 14.sp,
                                lineHeight = 20.sp,
                                modifier = Modifier.weight(1f),
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun SettingsPanel(
    settings: DisplaySettings,
    contentVersion: Int,
    syncStatus: ContentSyncStatus,
    onChange: (DisplaySettings) -> Unit,
    onRetry: () -> Unit = {},
) {
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
            Text(
                text = "Версия текста: $contentVersion · ${syncStatus.message}",
                color = if (syncStatus.isChecking) ReaderColors.Context else ReaderColors.Muted,
                fontSize = 12.sp,
                lineHeight = 17.sp,
            )
            if (syncStatus.canRetry) {
                OutlinedButton(
                    onClick = onRetry,
                    colors = ButtonDefaults.outlinedButtonColors(contentColor = ReaderColors.Context),
                    border = BorderStroke(1.dp, ReaderColors.Border),
                    contentPadding = PaddingValues(horizontal = 12.dp, vertical = 4.dp),
                ) {
                    Text("Обновить", fontSize = 13.sp)
                }
            }
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
            SettingRow("Объяснение перевода", settings.showComments) {
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
fun FieldLabel(text: String) {
    Text(
        text = text,
        color = ReaderColors.Muted,
        fontSize = 10.sp,
        fontWeight = FontWeight.SemiBold,
        letterSpacing = 0.5.sp,
        lineHeight = 14.sp,
    )
}

@Composable
fun LineCard(
    line: ReaderLine,
    settings: DisplaySettings,
    allLines: List<ReaderLine>,
    works: List<WorkIndex>,
    onOpenReference: (ReaderLine) -> Unit,
    onOpenWork: (String) -> Unit,
) {
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
                        Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                            FieldLabel("Транслитерация")
                            Text(text = line.roman, color = ReaderColors.Roman, fontSize = 14.sp)
                        }
                    }
                    if (settings.showAuthor && line.authorName.isNotBlank()) {
                        Text(
                            text = line.authorName,
                            color = ReaderColors.Muted,
                            fontSize = 13.sp,
                        )
                    }
                    if (settings.showTranslation && line.translation.isNotBlank()) {
                        Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                            FieldLabel("Перевод")
                            RichTextField(
                                text = line.translation,
                                color = ReaderColors.Translation,
                                fontSize = 17.sp,
                                lineHeight = 24.sp,
                                allLines = allLines,
                                works = works,
                                onOpenReference = onOpenReference,
                                onOpenWork = onOpenWork,
                            )
                        }
                    }
                    if (settings.showArtistic && !line.artistic.isNullOrBlank()) {
                        Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                            FieldLabel("Художественный")
                            RichTextField(
                                text = line.artistic,
                                color = ReaderColors.Artistic,
                                fontSize = 16.sp,
                                lineHeight = 23.sp,
                                allLines = allLines,
                                works = works,
                                onOpenReference = onOpenReference,
                                onOpenWork = onOpenWork,
                                prefix = "〜 ",
                            )
                        }
                    }
                    if (settings.showContext && !line.context.isNullOrBlank()) {
                        Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                            FieldLabel("Контекст")
                            RichTextField(
                                text = line.context,
                                color = ReaderColors.Context,
                                fontSize = 14.sp,
                                lineHeight = 20.sp,
                                allLines = allLines,
                                works = works,
                                onOpenReference = onOpenReference,
                                onOpenWork = onOpenWork,
                            )
                        }
                    }
                    if (settings.showComments && !line.comment.isNullOrBlank()) {
                        Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                            FieldLabel("Объяснение перевода")
                            ExplanationCard(
                                text = line.comment,
                                allLines = allLines,
                                works = works,
                                onOpenReference = onOpenReference,
                                onOpenWork = onOpenWork,
                            )
                        }
                    }
                }
            }
        }
    }
}

data class SggsReference(
    val url: String,
    val ang: Int,
    val lineNumber: Int,
    val quotedLines: List<String>,
)

data class WorkReference(
    val workId: String,
    val quotedLines: List<String>,
)

@Composable
fun ExplanationCard(
    text: String,
    allLines: List<ReaderLine>,
    works: List<WorkIndex>,
    onOpenReference: (ReaderLine) -> Unit,
    onOpenWork: (String) -> Unit,
) {
    Surface(
        color = ReaderColors.ExplanationBg,
        shape = RoundedCornerShape(6.dp),
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 10.dp, vertical = 8.dp),
        ) {
            RichTextField(
                text = text,
                color = ReaderColors.ExplanationText,
                fontSize = 13.sp,
                lineHeight = 19.sp,
                allLines = allLines,
                works = works,
                onOpenReference = onOpenReference,
                onOpenWork = onOpenWork,
            )
        }
    }
}

@Composable
fun WorkReferenceCard(
    reference: WorkReference,
    work: WorkIndex?,
    onOpenWork: (String) -> Unit,
) {
    Card(
        modifier = Modifier.fillMaxWidth().clickable { onOpenWork(reference.workId) },
        colors = CardDefaults.cardColors(containerColor = Color(0xFFF3EFE8)),
        shape = RoundedCornerShape(8.dp),
        border = BorderStroke(1.dp, ReaderColors.Border),
    ) {
        Column(Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
            reference.quotedLines.forEach { line ->
                Text(line, color = ReaderColors.Muted, fontSize = 14.sp, lineHeight = 20.sp)
            }
            if (work != null && work.gurmukhiTitle.isNotBlank()) {
                Text(
                    text = work.gurmukhiTitle,
                    color = ReaderColors.Gurmukhi,
                    fontSize = 17.sp,
                    fontWeight = FontWeight.Medium,
                )
            }
            Text(
                text = work?.title ?: reference.workId,
                color = ReaderColors.Ink,
                fontWeight = FontWeight.SemiBold,
                fontSize = 15.sp,
            )
            Text(
                text = "Открыть →",
                color = ReaderColors.Context,
                fontSize = 12.sp,
                fontWeight = FontWeight.SemiBold,
            )
        }
    }
}

@Composable
fun RichTextField(
    text: String,
    color: Color,
    fontSize: androidx.compose.ui.unit.TextUnit,
    lineHeight: androidx.compose.ui.unit.TextUnit,
    allLines: List<ReaderLine>,
    works: List<WorkIndex>,
    onOpenReference: (ReaderLine) -> Unit,
    onOpenWork: (String) -> Unit,
    prefix: String = "",
    fontStyle: FontStyle = FontStyle.Normal,
) {
    val blocks = splitSggsReferenceBlocks(prefix + text)
    Column(verticalArrangement = Arrangement.spacedBy(7.dp)) {
        blocks.forEach { block ->
            val workRef = parseWorkReferenceBlock(block)
            val sggsRef = if (workRef == null) parseSggsReferenceBlock(block) else null
            when {
                workRef != null -> WorkReferenceCard(
                    reference = workRef,
                    work = works.firstOrNull { it.id == workRef.workId },
                    onOpenWork = onOpenWork,
                )
                sggsRef != null -> SggsReferenceCard(
                    reference = sggsRef,
                    targetLine = allLines.firstOrNull {
                        it.ang == sggsRef.ang && it.lineNumber == sggsRef.lineNumber
                    },
                    onOpenReference = onOpenReference,
                )
                else -> {
                    val rich = richTextToAnnotatedString(block, color)
                    if (rich.isNotBlank()) {
                        Text(
                            text = rich,
                            color = color,
                            fontSize = fontSize,
                            lineHeight = lineHeight,
                            fontStyle = fontStyle,
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun SggsReferenceCard(
    reference: SggsReference,
    targetLine: ReaderLine?,
    onOpenReference: (ReaderLine) -> Unit,
) {
    val cardModifier = if (targetLine != null) {
        Modifier
            .fillMaxWidth()
            .clickable { onOpenReference(targetLine) }
    } else {
        Modifier.fillMaxWidth()
    }
    Card(
        modifier = cardModifier,
        colors = CardDefaults.cardColors(containerColor = Color(0xFFF1F6EF)),
        shape = RoundedCornerShape(8.dp),
        border = BorderStroke(1.dp, Color(0xFFC9DDC1)),
    ) {
        Column(Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(5.dp)) {
            val quote = if (reference.quotedLines.isNotEmpty()) {
                reference.quotedLines
            } else {
                listOfNotNull(
                    targetLine?.gurmukhi,
                    targetLine?.roman,
                    targetLine?.translation,
                ).filter { it.isNotBlank() }
            }
            quote.forEachIndexed { index, line ->
                Text(
                    text = stripRichText(line),
                    color = when (index) {
                        0 -> ReaderColors.Gurmukhi
                        1 -> ReaderColors.Roman
                        else -> ReaderColors.Translation
                    },
                    fontSize = when (index) {
                        0 -> 18.sp
                        1 -> 13.sp
                        else -> 14.sp
                    },
                    lineHeight = when (index) {
                        0 -> 25.sp
                        1 -> 19.sp
                        else -> 20.sp
                    },
                    fontWeight = if (index == 0) FontWeight.Medium else FontWeight.Normal,
                )
            }
            Text(
                text = "Анг ${reference.ang} · строка ${reference.lineNumber}" +
                    if (targetLine == null) " · открыть на сайте" else "",
                color = ReaderColors.Context,
                fontSize = 12.sp,
                fontWeight = FontWeight.SemiBold,
            )
        }
    }
}

fun richTextToAnnotatedString(text: String, baseColor: Color) = buildAnnotatedString {
    val normalized = normalizeRichTextBreaks(text)
    val tokenPattern = Regex("""(?is)<(/?)(strong|b|em|i)>|\[\[([\s\S]*?)\]\]""")
    var cursor = 0
    val styleStack = mutableListOf<SpanStyle>()
    tokenPattern.findAll(normalized).forEach { match ->
        val segmentDecoded = decodeHtml(normalized.substring(cursor, match.range.first))
        appendWithStack(segmentDecoded, styleStack)
        val contextText = match.groups[3]?.value
        if (contextText != null) {
            val afterIdx = match.range.last + 1
            val afterChar = if (afterIdx < normalized.length) normalized[afterIdx] else ' '
            if (segmentDecoded.isNotEmpty() && !segmentDecoded.last().isWhitespace()) append(" ")
            pushStyle(SpanStyle(color = ReaderColors.Context))
            append(decodeHtml(contextText))
            pop()
            if (!afterChar.isWhitespace() && afterChar !in ".,;:!?)»—") append(" ")
        } else {
            val isClosing = match.groups[1]?.value == "/"
            val tag = match.groups[2]?.value?.lowercase().orEmpty()
            if (isClosing) {
                if (styleStack.isNotEmpty()) styleStack.removeAt(styleStack.lastIndex)
            } else {
                val style = when (tag) {
                    "strong", "b" -> SpanStyle(fontWeight = FontWeight.Bold)
                    "em", "i" -> SpanStyle(fontStyle = FontStyle.Italic)
                    else -> SpanStyle(color = baseColor)
                }
                styleStack += style
            }
        }
        cursor = match.range.last + 1
    }
    appendWithStack(decodeHtml(normalized.substring(cursor)), styleStack)
}

private fun androidx.compose.ui.text.AnnotatedString.Builder.appendWithStack(
    text: String,
    styles: List<SpanStyle>,
) {
    styles.forEach { pushStyle(it) }
    append(text)
    repeat(styles.size) { pop() }
}

fun normalizeRichTextBreaks(text: String): String =
    text.replace("\r\n", "\n")
        .replace("\r", "\n")
        .replace(Regex("""(?i)<br\s*/?>"""), "\n")
        .replace(Regex("""(?i)</p>\s*<p[^>]*>"""), "\n")
        .replace(Regex("""(?i)</?(p|div)[^>]*>"""), "\n")
        .trim()

fun stripRichText(text: String): String =
    decodeHtml(
        normalizeRichTextBreaks(text)
            .replace(Regex("""(?is)<[^>]+>"""), "")
            .replace("[[", "")
            .replace("]]", "")
    ).trim()

fun decodeHtml(text: String): String {
    if (!text.contains('<') && !text.contains('&')) return text
    return text.split('\n').joinToString("\n") { segment ->
        Html.fromHtml(segment, Html.FROM_HTML_MODE_LEGACY).toString().trimEnd()
    }
}

private val ANCHOR_REGEX = Regex("""(?is)<a\s+href=["'][^"']+["'][^>]*>.*?</a>""")

fun splitSggsReferenceBlocks(text: String): List<String> {
    val normalized = normalizeRichTextBreaks(text)
    return normalized.split(Regex("""\n{2,}"""))
        .map { it.trim() }
        .filter { it.isNotBlank() }
        .flatMap { splitAroundAnchors(it) }
}

private fun splitAroundAnchors(paragraph: String): List<String> {
    val result = mutableListOf<String>()
    var cursor = 0
    ANCHOR_REGEX.findAll(paragraph).forEach { match ->
        val before = paragraph.substring(cursor, match.range.first).trim()
        if (before.isNotBlank()) result += before
        result += match.value.trim()
        cursor = match.range.last + 1
    }
    val after = paragraph.substring(cursor).trim()
    if (after.isNotBlank()) result += after
    return if (result.isEmpty()) listOf(paragraph) else result
}

fun parseSggsReferenceBlock(block: String): SggsReference? {
    val lines = block.lines().map { it.trim() }.filter { it.isNotBlank() }
    if (lines.isEmpty()) return null
    // Plain URL format: URL is the last line
    val plainParsed = parseSggsUrl(lines.last())
    if (plainParsed != null) {
        return SggsReference(
            url = lines.last(),
            ang = plainParsed.first,
            lineNumber = plainParsed.second,
            quotedLines = lines.dropLast(1),
        )
    }
    // Anchor tag format: <a href="https://...?ang=N&line=N">anchor text</a>
    val anchorMatch = Regex("""(?is)<a\s+href=["']([^"']+)["'][^>]*>(.*?)</a>""").find(block)
        ?: return null
    val href = anchorMatch.groupValues[1]
    val anchorParsed = parseSggsUrl(href) ?: return null
    val linkText = anchorMatch.groupValues[2].trim()
    return SggsReference(
        url = href,
        ang = anchorParsed.first,
        lineNumber = anchorParsed.second,
        quotedLines = if (linkText.isNotBlank()) listOf(linkText) else emptyList(),
    )
}

fun parseSggsUrl(url: String): Pair<Int, Int>? {
    return runCatching {
        val uri = Uri.parse(url)
        val ang = uri.getQueryParameter("ang")?.toIntOrNull()
        val line = uri.getQueryParameter("line")?.toIntOrNull()
        if (ang != null && line != null) ang to line else null
    }.getOrNull()
}

fun parseWorkUrl(url: String): String? =
    runCatching { Uri.parse(url).getQueryParameter("work") }
        .getOrNull()
        ?.takeIf { it.isNotBlank() }

fun parseWorkReferenceBlock(block: String): WorkReference? {
    val lines = block.lines().map { it.trim() }.filter { it.isNotBlank() }
    if (lines.isEmpty()) return null
    val workId = parseWorkUrl(lines.last()) ?: return null
    return WorkReference(workId = workId, quotedLines = lines.dropLast(1))
}

private fun parseReaderLines(root: JSONObject): List<ReaderLine> {
    val lines = mutableListOf<ReaderLine>()
    val angs = root.optJSONArray("angs") ?: return lines
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
    return lines
}

private fun computeLineDiffs(oldLines: List<ReaderLine>, newLines: List<ReaderLine>): List<LineDiff> {
    val oldById = oldLines.associateBy { it.id }
    return newLines.mapNotNull { newLine ->
        val oldLine = oldById[newLine.id] ?: return@mapNotNull null
        val fields = mutableListOf<FieldDiff>()
        if (oldLine.translation != newLine.translation && newLine.translation.isNotBlank())
            fields += FieldDiff("Перевод", oldLine.translation, newLine.translation)
        if (oldLine.artistic != newLine.artistic && !newLine.artistic.isNullOrBlank())
            fields += FieldDiff("Художественный", oldLine.artistic.orEmpty(), newLine.artistic.orEmpty())
        if (oldLine.context != newLine.context && !newLine.context.isNullOrBlank())
            fields += FieldDiff("Контекст", oldLine.context.orEmpty(), newLine.context.orEmpty())
        if (fields.isEmpty()) null
        else LineDiff(
            lineId = newLine.id,
            ang = newLine.ang,
            workId = newLine.workId,
            workTitle = newLine.workTitle,
            gurmukhi = newLine.gurmukhi,
            changedFields = fields,
        )
    }
}

private fun saveContentDiff(context: Context, diffs: List<LineDiff>) {
    val arr = JSONArray()
    diffs.forEach { diff ->
        val obj = JSONObject()
        obj.put("lineId", diff.lineId)
        obj.put("ang", diff.ang)
        obj.put("workId", diff.workId)
        obj.put("workTitle", diff.workTitle)
        obj.put("gurmukhi", diff.gurmukhi)
        val fields = JSONArray()
        diff.changedFields.forEach { f ->
            val fObj = JSONObject()
            fObj.put("label", f.label)
            fObj.put("old", f.old)
            fObj.put("new", f.new)
            fields.put(fObj)
        }
        obj.put("fields", fields)
        arr.put(obj)
    }
    File(context.filesDir, "nitnem_content_diff.json").writeText(arr.toString(), Charsets.UTF_8)
}

private fun loadContentDiff(context: Context): List<LineDiff> =
    runCatching {
        val text = File(context.filesDir, "nitnem_content_diff.json").readText(Charsets.UTF_8)
        val arr = JSONArray(text)
        buildList {
            for (i in 0 until arr.length()) {
                val obj = arr.getJSONObject(i)
                val fields = obj.getJSONArray("fields")
                add(LineDiff(
                    lineId = obj.getString("lineId"),
                    ang = obj.getInt("ang"),
                    workId = obj.getString("workId"),
                    workTitle = obj.getString("workTitle"),
                    gurmukhi = obj.getString("gurmukhi"),
                    changedFields = buildList {
                        for (j in 0 until fields.length()) {
                            val f = fields.getJSONObject(j)
                            add(FieldDiff(f.getString("label"), f.getString("old"), f.getString("new")))
                        }
                    },
                ))
            }
        }
    }.getOrDefault(emptyList())

fun loadNitnemContent(context: Context): NitnemContent {
    val text = context.loadBestNitnemContentText()
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

    val lines = parseReaderLines(root)

    return NitnemContent(
        title = bani.optString("title", "Nitnem Authentic"),
        subtitle = bani.optString("subtitle", "Первые 13 ангов СГГС"),
        packageId = root.optString("package_id", NITNEM_PACKAGE_ID),
        schemaVersion = root.optInt("schema_version", 1),
        contentVersion = root.optInt("content_version", 1),
        generatedAt = root.optString("generated_at"),
        infoBlocks = infoBlocks,
        updatesMarkdown = context.loadAssetTextOrBlank("updates.md"),
        conceptMarkdown = context.loadAssetTextOrBlank("ek_granth_maryada.md"),
        appInfoMarkdown = context.loadAssetTextOrBlank("app_info.md"),
        dictionaryMarkdown = context.loadAssetTextOrBlank("dictionary.md"),
        works = works,
        lines = lines,
    )
}

private fun Context.loadBestNitnemContentText(): String {
    val bundledText = assets.open(NITNEM_CONTENT_FILE)
        .bufferedReader(Charsets.UTF_8)
        .use { it.readText() }
    val cachedFile = File(filesDir, NITNEM_CONTENT_FILE)
    if (!cachedFile.isFile) return bundledText

    val cachedText = runCatching { cachedFile.readText(Charsets.UTF_8) }.getOrNull()
        ?: return bundledText
    val bundledVersion = runCatching { JSONObject(bundledText).optInt("content_version", 1) }
        .getOrDefault(1)
    val cachedVersion = runCatching { JSONObject(cachedText).optInt("content_version", 0) }
        .getOrDefault(0)
    return if (cachedVersion >= bundledVersion) cachedText else bundledText
}

private fun fetchManifestWithFallback(localContentVersion: Int): Pair<String, String> {
    val query = "/manifest?package_id=$NITNEM_PACKAGE_ID&content_version=$localContentVersion"
    var lastError: Exception? = null
    for (base in NITNEM_API_BASES) {
        try {
            return base to readUrlText("$base$query")
        } catch (e: java.io.IOException) {
            lastError = e
        }
    }
    throw lastError!!
}

private fun checkAndUpdateNitnemContent(
    context: Context,
    localContentVersion: Int,
): ContentSyncResult = runCatching {
    val (base, manifestText) = fetchManifestWithFallback(localContentVersion)
    val manifest = JSONObject(manifestText)
    val remotePackageId = manifest.optString("package_id")
    if (remotePackageId != NITNEM_PACKAGE_ID) {
        return@runCatching ContentSyncResult.Skipped("Сервер вернул другой пакет текста")
    }

    val remoteVersion = manifest.optInt("content_version", localContentVersion)
    if (remoteVersion <= localContentVersion || !manifest.optBoolean("has_update", true)) {
        return@runCatching ContentSyncResult.UpToDate
    }

    val packageUrl = manifest.optString("package_url")
        .ifBlank { "$base/package/$NITNEM_PACKAGE_ID" }
    val packageText = readUrlText(packageUrl)
    val expectedSha256 = manifest.optString("sha256").ifBlank { null }
    if (expectedSha256 != null && packageText.sha256() != expectedSha256.lowercase()) {
        return@runCatching ContentSyncResult.Skipped("Обновление не прошло проверку checksum")
    }

    val packageRoot = JSONObject(packageText)
    if (packageRoot.optString("package_id") != NITNEM_PACKAGE_ID) {
        return@runCatching ContentSyncResult.Skipped("Получен неподходящий пакет текста")
    }
    if (packageRoot.optInt("content_version", 0) != remoteVersion) {
        return@runCatching ContentSyncResult.Skipped("Версия пакета не совпала с manifest")
    }

    val diffs = runCatching {
        val oldLines = parseReaderLines(JSONObject(context.loadBestNitnemContentText()))
        val newLines = parseReaderLines(JSONObject(packageText))
        computeLineDiffs(oldLines, newLines)
    }.getOrDefault(emptyList())

    File(context.filesDir, NITNEM_CONTENT_FILE).writeText(packageText, Charsets.UTF_8)
    if (diffs.isNotEmpty()) saveContentDiff(context, diffs)
    context.getSharedPreferences("nitnem_content_sync", Context.MODE_PRIVATE)
        .edit()
        .putInt("content_version", remoteVersion)
        .putString("updated_at", manifest.optString("updated_at"))
        .putLong("checked_at_ms", System.currentTimeMillis())
        .apply()
    ContentSyncResult.Updated(remoteVersion, diffs)
}.getOrElse { error ->
    ContentSyncResult.Skipped("Не удалось проверить обновления: ${error.message ?: "нет сети"}")
}

private fun readUrlText(url: String): String {
    val connection = URL(url).openConnection()
    connection.connectTimeout = 7000
    connection.readTimeout = 10000
    return connection.getInputStream()
        .bufferedReader(Charsets.UTF_8)
        .use { it.readText() }
}

private fun String.sha256(): String {
    val digest = MessageDigest.getInstance("SHA-256")
        .digest(toByteArray(Charsets.UTF_8))
    return digest.joinToString(separator = "") { byte -> "%02x".format(byte) }
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
