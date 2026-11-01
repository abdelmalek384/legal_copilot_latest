"""Regression checks for the Arabic-first single-page frontend's accessibility contract."""
from pathlib import Path
import unittest

HTML = Path("static/index.html").read_text(encoding="utf-8")

class FrontendUXContractTests(unittest.TestCase):
    def test_skip_link_and_main_landmark_are_present(self):
        self.assertIn("className:'skip-link'", HTML)
        self.assertIn("id:'main',tabIndex:-1", HTML)
        self.assertIn("aria-label':navLabel('التنقل الرئيسي','Primary navigation')", HTML)

    def test_local_browser_reminders_are_opt_in_and_privacy_preserving(self):
        self.assertIn("Enable reminders", HTML)
        self.assertIn("Notification.requestPermission()", HTML)
        self.assertIn("lc_local_reminder_sent_", HTML)
        self.assertIn("They do not run after the browser closes", HTML)
        self.assertIn("notifications never include case names", HTML)
        self.assertIn("15*60*1000", HTML)

    def test_admin_audit_export_entrypoint_is_present(self):
        self.assertIn("/audit/security-events.csv", HTML)
        self.assertIn("Download security audit CSV", HTML)
        self.assertIn("تصدير سجل الأمان", HTML)

    def test_navigation_is_keyboard_operable_and_announces_current_page(self):
        self.assertIn("role:'button',tabIndex:0,'aria-current':PAGE===id?'page':null", HTML)
        self.assertIn("e.key==='Enter'||e.key===' '", HTML)

    def test_language_switch_rerenders_every_primary_workspace(self):
        switch = HTML[HTML.index("function switchLanguage()"):HTML.index("\nconst languageObserver")]
        for page in ("dash", "clients", "cases", "tasks", "calendar", "law", "coverage", "review", "settings"):
            self.assertIn("PAGE==='" + page + "'", switch)
        self.assertIn("if(!ME.id){login(AUTH_MODE)", switch)

    def test_case_tabs_summary_team_and_activity_follow_selected_language(self):
        self.assertIn("uiText('الملخص','Overview')", HTML)
        self.assertIn("uiText('الحالة: ','Status: ')", HTML)
        self.assertIn("uiText('جلسة','Hearing')", HTML)
        self.assertIn("uiText(RL[m.role]||m.role,m.role==='lead'?'Lead':m.role==='associate'?'Associate':'Junior')", HTML)
        self.assertIn("uiText('إزالة هذا العضو من القضية؟','Remove this member from the case?')", HTML)
        self.assertIn("toLocaleString(LANG==='ar'?'ar-EG':'en-US'", HTML)

    def test_document_review_workflow_labels_follow_selected_language(self):
        self.assertIn("uiText('اعتماد النص المستخرج','Accept extracted text')", HTML)
        self.assertIn("uiText('يحتاج إعادة فحص','Needs recheck')", HTML)
        self.assertIn("uiText('حفظ التصحيح','Save correction')", HTML)
        self.assertIn("uiText('النص المستخرج — للقراءة فقط','Extracted text — read only')", HTML)
        self.assertIn("uiText('نص OCR غير متحقق','OCR text not verified')", HTML)
        self.assertIn("uiText('جارٍ تحميل المقاطع…','Loading text chunks…')", HTML)
        self.assertIn("uiText('PDF أو Word حتى 15 ميجابايت. النص المستخرج فقط هو المفهرس؛ لا تحفظ نسخة الملف الأصلي. راجع المقاطع قبل الاعتماد عليها، خصوصاً نص OCR.','PDF or Word up to 15 MB. Only extracted text is indexed; the original file is not retained. Review chunks before relying on them, especially OCR text.')", HTML)

    def test_case_detail_inputs_and_validation_follow_selected_language(self):
        self.assertIn("uiText('رقم القضية','Case number')", HTML)
        self.assertIn("uiText('مهمة جديدة','New task')", HTML)
        self.assertIn("uiText('ملاحظة (المحكمة، الدائرة، الغرض)','Note (court, circuit, purpose)')", HTML)
        self.assertIn("uiText('نوع الموعد (استئناف، طعن، تقديم مستند...)','Deadline type (appeal, challenge, filing...)')", HTML)
        self.assertIn("uiText('وصف الأتعاب','Fee description')", HTML)
        self.assertIn("uiText('الإجمالي ','Total ')", HTML)
        self.assertIn("uiText('أدخل نوع الموعد وتاريخه','Enter the deadline type and date')", HTML)

    def test_new_case_and_client_views_follow_selected_language(self):
        self.assertIn("uiText('عنوان القضية','Case title')", HTML)
        self.assertIn("uiText('حفظ القضية','Save case')", HTML)
        self.assertIn("uiText('العملاء','Clients')", HTML)
        self.assertIn("uiText('فحص أولي لتعارض المصالح','Preliminary conflict check')", HTML)
        self.assertIn("uiText('أدخل حرفين على الأقل','Enter at least two characters')", HTML)
        self.assertIn("uiText('بدون مرحلة','No stage')", HTML)

    def test_modal_traps_keyboard_focus_and_restores_opener(self):
        self.assertIn("function closeModal(overlay)", HTML)
        self.assertIn("overlay.__focusReturn=opener", HTML)
        self.assertIn("if(e.key!=='Tab')return", HTML)
        self.assertIn("focusables[focusables.length-1]", HTML)
        self.assertIn("last.focus()", HTML)
        self.assertIn("if(opener&&opener.isConnected&&typeof opener.focus==='function')opener.focus()", HTML)

    def test_modal_escape_and_reduced_motion_support(self):
        self.assertIn("document.addEventListener('keydown'", HTML)
        self.assertIn("e.key==='Escape'", HTML)
        self.assertIn("@media(prefers-reduced-motion:reduce)", HTML)

    def test_research_scope_is_explicit_and_metadata_discovery_is_separate(self):
        self.assertIn("value:'verified_corpus'", HTML)
        self.assertIn("value:'firm_documents'", HTML)
        self.assertIn("value:'metadata_only'", HTML)
        self.assertIn("'/research/discover'", HTML)
        self.assertIn("Select a matter to search firm documents", HTML)

    def test_element_helper_sets_aria_data_and_role_attributes(self):
        self.assertIn("key==='role'||key.startsWith('aria-')||key.startsWith('data-')", HTML)
        self.assertIn("e.setAttribute(key,String(value))", HTML)
        self.assertIn("if(value!=null)e.setAttribute", HTML)

    def test_corpus_review_navigation_matches_server_authorization(self):
        self.assertIn("...(ME.can_review_legal?[['coverage'", HTML)
        self.assertIn("if(!ME.can_review_legal)", HTML)
        self.assertIn('"can_review_legal": _user_can_review_legal', Path("app.py").read_text(encoding="utf-8"))

    def test_corpus_coverage_metrics_have_definitions_and_catalog_drilldowns(self):
        self.assertIn("Count of registered source records, not verified laws.", HTML)
        self.assertIn("Instruments without a registered version record.", HTML)
        self.assertIn("openCatalog('sources')", HTML)
        self.assertIn("openCatalog('documents')", HTML)
        self.assertIn("openCatalog('metadata_only_documents')", HTML)
        self.assertIn("window.COVERAGE_QUEUE_FILTER='all_versions'", HTML)
        self.assertIn("safeHttpsUrl(item.source_page)", HTML)
        self.assertIn("filters.collection_permission", HTML)
        self.assertIn("filters.commercial_reuse_permission", HTML)
        self.assertIn("View sources with permission state ", HTML)
        self.assertIn("openCatalog('sources','',{collection_permission:r.collection_permission||'unknown'", HTML)
        self.assertIn("central_permission_register_blocked_versions", HTML)
        self.assertIn("versions_not_eligible_for_verified_answers", HTML)
        self.assertIn("same source-eligibility gate", HTML)

    def test_corpus_registry_drilldowns_can_search_beyond_the_first_page(self):
        self.assertIn("const openCatalog=async(kind,query='',filters={})=>", HTML)
        self.assertIn("q='+encodeURIComponent(query)", HTML)
        self.assertIn("Search title, ID, or authority", HTML)
        self.assertIn("Search source and instrument registry", HTML)
        self.assertIn("e.key==='Enter'){e.preventDefault();openCatalog(kind,searchInput.value,filters)", HTML)

    def test_review_queue_rejects_unsafe_source_links_and_explains_missing_gates(self):
        self.assertIn("const versionUrl=safeHttpsUrl(v.source_url)", HTML)
        self.assertIn("No safe HTTPS source URL is recorded.", HTML)
        self.assertIn("Gates not met: ", HTML)
        self.assertIn("v.version_permission_evidence", HTML)
        self.assertIn("v.source_permission_evidence", HTML)
        self.assertIn("v.source_permission_register_ready", HTML)
        self.assertIn("v.answer_eligible===true", HTML)
        self.assertIn("central permission register match and rights-evidence URLs", HTML)
        self.assertIn("independent source/lawyer verification is still required", HTML)

    def test_source_status_labels_have_plain_language_explanations_and_original_host(self):
        self.assertIn("const statusDescriptions={", HTML)
        self.assertIn("not independently verified as law", HTML)
        self.assertIn("does not prove no applicable law exists", HTML)
        self.assertIn("sourceHostLabel(recordedSource)", HTML)

    def test_research_highlighting_uses_actual_matched_surface_terms(self):
        self.assertIn("const highlightTerms=(text,question,matchedTerms)=>", HTML)
        self.assertIn("highlightTerms(s.text||'',sourceQuestion,s.matched_terms)", HTML)

    def test_research_empty_state_reads_scope_from_message_result(self):
        self.assertIn("const messageScope=(m.result&&m.result.scope)||m.scope||'unknown'", HTML)
        self.assertIn("messageScope==='metadata_only'", HTML)
        self.assertIn("messageScope==='firm_documents'", HTML)
        self.assertIn("messageScope==='verified_corpus'", HTML)
        self.assertIn("if(messageScope!=='metadata_only')actions.append", HTML)
        self.assertIn("const messageQuestion=messages.slice(0,messageIndex).reverse().find(x=>x.role==='user')?.content||priorQuestion||''", HTML)
        self.assertIn("api('/research/discover','POST',{q:messageQuestion}),messageQuestion", HTML)

    def test_research_empty_state_copy_matches_selected_scope(self):
        self.assertIn("No matching source-catalog metadata was returned; this search does not retrieve legal text.", HTML)
        self.assertIn("No relevant passage was returned from the selected matter documents.", HTML)
        self.assertIn("No relevant verified legal text was returned by this verified-corpus search.", HTML)
        self.assertIn("No source records were returned; the search scope was not recorded.", HTML)
        self.assertIn("if(messageScope!=='metadata_only')actions.append", HTML)

    def test_research_async_status_and_toasts_are_announced(self):
        self.assertIn('id="toast" role="status" aria-live="polite" aria-atomic="true"', HTML)
        self.assertIn("role:'status','aria-live':'polite','aria-atomic':'true'", HTML)
        self.assertIn("Searching sources…", HTML)
        self.assertIn("Research complete. Review the answer and sources.", HTML)
        self.assertIn("Found '+count+' metadata-only source records.", HTML)

    def test_registered_source_links_show_host_and_reject_url_credentials(self):
        self.assertIn("u.protocol==='https:'&&!u.username&&!u.password", HTML)
        self.assertIn("const sourceHostLabel=v=>", HTML)
        self.assertIn("sourceHostLabel(sourceUrl)", HTML)
        self.assertIn("sourceHostLabel(source)", HTML)
        self.assertIn("rel:'noopener noreferrer'", HTML)

    def test_copy_fallback_checks_result_and_always_removes_temporary_textarea(self):
        self.assertIn("copied=document.execCommand('copy')===true", HTML)
        self.assertIn("finally{t.remove()}", HTML)
        self.assertIn("if(!copied)throw new Error('copy failed')", HTML)

    def test_memo_export_filename_does_not_invent_today_for_missing_or_invalid_date(self):
        export_memo = HTML[HTML.index("const exportMemo="):HTML.index("const renderDiscovery=")]
        self.assertIn("exportDate=typeof raw==='string'", export_memo)
        self.assertIn("&&/^\\d{4}-\\d{2}-\\d{2}$/", export_memo)
        self.assertIn("?raw:'unknown'", export_memo)
        self.assertIn("download:'legal-research-memo-'+exportDate+'.txt'", export_memo)
        self.assertNotIn("setTimeout(()=>URL.revokeObjectURL(url),1000)};document.body.append(a)", export_memo)
        self.assertNotIn("result.requested_as_of||new Date()", export_memo)

    def test_memo_export_uses_recorded_scope_or_unknown_not_current_selector(self):
        memo = HTML[HTML.index("const memoText="):HTML.index("const exportMemo=")]
        self.assertIn("memoScope=typeof result.scope==='string'&&result.scope.trim()?result.scope:'unknown'", memo)
        self.assertIn("rawAsOf=result.requested_as_of", memo)
        self.assertIn("/^\\d{4}-\\d{2}-\\d{2}$/", memo)
        self.assertIn("?rawAsOf:'unknown'", memo)
        self.assertIn("asOf==='unknown'?'- The search as-of date was not recorded; do not infer current legal status.'", memo)
        self.assertIn("'Search scope: '+memoScope", memo)
        self.assertNotIn("scopeSelect.value", memo)
        self.assertIn("Array.isArray(result.sources)?result.sources:[]", memo)
        self.assertIn("typeof source.text==='string'&&source.text.trim()?source.text:'(No passage text recorded; metadata-only result.)'", memo)
        self.assertIn("x&&typeof x==='object'&&!Array.isArray(x)?x:{}", memo)
        self.assertNotIn("x.text||'(No passage text recorded; metadata-only result.)'", memo)
        self.assertIn("firm_documents:'No relevant passage was returned from the selected matter documents.'", memo)
        self.assertIn("metadata_only:'No matching source-catalog metadata was returned; this search did not retrieve legal text.'", memo)
        self.assertIn("unknown:'No source records were returned; the search scope was not recorded.'", memo)
        self.assertNotIn("No relevant verified passage was found in this search scope.", memo)

    def test_research_inspector_displays_only_latest_review_events(self):
        self.assertIn("const latestReviewByType=Object.create(null)", HTML)
        self.assertIn("const parseReviewTime=value=>", HTML)
        self.assertIn("Date.parse(raw.replace(' ','T')+'Z')", HTML)
        self.assertIn("const eventTime=parseReviewTime(event.reviewed_at)", HTML)
        self.assertIn("eventTime===previousTime&&eventId>previousId", HTML)
        self.assertIn(":eventId>previousId", HTML)
        self.assertIn("const lawyerApproval=latestReviewByType.lawyer_approval", HTML)
        self.assertIn("Latest recorded lawyer review: ", HTML)
        self.assertIn("const ev=latestReviews.filter(e=>e.evidence_url)", HTML)
        self.assertNotIn("(p.review_evidence||[]).find(e=>e.review_type==='lawyer_approval'&&e.outcome==='pass'", HTML)
        self.assertNotIn("(p.review_evidence||[]).filter(e=>e.outcome==='pass'&&e.evidence_url)", HTML)

    def test_source_inspector_exposes_status_pin_cites_copy_and_memo_actions(self):
        self.assertIn("source_status", HTML)
        self.assertIn("s.article", HTML)
        self.assertIn("Copy citation", HTML)
        self.assertIn("Copy exact passage", HTML)
        self.assertIn("highlightTerms", HTML)
        self.assertIn("document.createTextNode", HTML)
        self.assertIn("Export research memo", HTML)
        self.assertIn("setTimeout(()=>URL.revokeObjectURL(url),1000)", HTML)
        self.assertIn("save-to-matter", HTML)
        self.assertIn("No relevant verified legal text was returned by this verified-corpus search.", HTML)
        self.assertNotIn("matterSelect.disabled", HTML)

    def test_multi_firm_switcher_and_corpus_navigation_use_server_checked_capabilities(self):
        self.assertIn("api('/session/firm','POST'", HTML)
        self.assertIn("Array.isArray(ME.firms)", HTML)
        self.assertIn("ME.can_review_legal", HTML)
        self.assertIn('"can_review_legal": _user_can_review_legal', Path("app.py").read_text(encoding="utf-8"))

    def test_focus_and_small_screen_rules_exist(self):
        self.assertIn(":focus-visible", HTML)
        self.assertIn("@media(max-width:420px)", HTML)
        self.assertIn("@media(forced-colors:active)", HTML)

    def test_primary_navigation_uses_a_nav_landmark(self):
        self.assertIn("h('nav',{className:'primary-nav'", HTML)

    def test_mobile_controls_and_body_copy_meet_readability_targets(self):
        self.assertIn("min-height:44px", HTML)
        self.assertIn(".mut{color:var(--mut);font-size:14px}", HTML)
        self.assertIn(".stat span{color:var(--mut);font-size:14px}", HTML)
        self.assertIn("overflow-x:auto;overscroll-behavior-inline:contain", HTML)

    def test_signup_tab_is_named_request_an_account(self):
        self.assertIn("textContent:LANG==='ar'?'طلب حساب':'Request an account'", HTML)

    def test_deadline_preview_persists_an_audit_summary_and_draft_warning(self):
        self.assertIn("Draft — not verified by a lawyer", HTML)
        self.assertIn("Calculation steps: ", HTML)
        self.assertIn("(result.steps_ar||[]).join(' | ')", HTML)

if __name__ == "__main__":
    unittest.main()
