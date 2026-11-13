"""Regression checks for the Arabic-first single-page frontend's accessibility contract."""
from pathlib import Path
import json
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "static" / "index.html").read_text(encoding="utf-8")

class FrontendUXContractTests(unittest.TestCase):

    def test_matter_csv_import_uses_strict_utf8_decoder(self):
        self.assertIn("new TextDecoder('utf-8',{fatal:true}).decode(await file.arrayBuffer())", HTML)
        self.assertIn("The file must use valid UTF-8 encoding", HTML)
        cases_page = HTML[HTML.index("async function casesPage(){"):HTML.index("\nasync function corpusCoverage()")]
        self.assertNotIn("csv:await file.text()", cases_page)

    def test_firm_mfa_policy_controls_are_visible_and_accessibly_named(self):
        self.assertIn("Firm MFA policy", HTML)
        self.assertIn("Require MFA for firm administrators", HTML)
        self.assertIn("Require MFA for everyone in the firm", HTML)
        self.assertIn("/admin/security-policy", HTML)
        self.assertIn("'aria-label':uiText('إلزام مسؤولي المكتب بتفعيل المصادقة'", HTML)
        self.assertIn("const session=await api('/session')", HTML)
        self.assertIn("if(ME.mfa_enrollment_required){mfaEnrollmentPage();return}", HTML)
        self.assertIn("if(ME.mfa_verification_required){mfaChallengePage();return}", HTML)
        self.assertIn("function mfaFirmSwitcher()", HTML)
        self.assertEqual(HTML.count("const firmSwitcher=mfaFirmSwitcher();if(firmSwitcher)card.append(firmSwitcher)"), 2)

    def test_mobile_language_switch_meets_44px_touch_target(self):
        self.assertIn("#side .lang-switch button { width: auto; min-width: 78px; min-height: 44px;", HTML)

    def test_case_discovery_uses_server_search_and_bounded_pagination(self):
        self.assertIn("/cases/search?", HTML)
        self.assertIn("limit:String(limit)", HTML)
        self.assertIn("offset:String(offset)", HTML)
        self.assertIn("previous.disabled=offset===0", HTML)
        self.assertIn("next.disabled=offset+limit>=total", HTML)

    def test_matter_csv_import_is_admin_only_and_bounded(self):
        self.assertIn("/cases/import.csv", HTML)
        self.assertIn("ME.role==='admin'", HTML)
        self.assertIn("accept:'.csv,text/csv'", HTML)
        self.assertIn("file.size>1000000", HTML)

    def test_case_team_tab_shows_workload_counts_and_unassigned_tasks(self):
        self.assertIn("Team workload", HTML)
        self.assertIn("open tasks", HTML)
        self.assertIn("completed tasks", HTML)
        self.assertIn("Unassigned tasks", HTML)
        self.assertIn("c.tasks.filter(task=>Number(task.assignee)===Number(member.user_id))", HTML)

    def test_arabic_ui_review_catalog_covers_source_literals(self):
        catalog_path = ROOT / "static" / "ar-ui-review.json"
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        entries = catalog["entries"]
        reviewed = {entry["arabic"] for entry in entries}
        self.assertEqual(catalog["entry_count"], len(entries))
        self.assertGreaterEqual(len(entries), 800)
        self.assertEqual(len(reviewed), len(entries))
        ids = {entry["id"] for entry in entries}
        self.assertEqual(len(ids), len(entries))
        self.assertTrue(all(
            isinstance(entry["source_lines"], list)
            and len(entry["source_lines"]) >= 1
            and all(isinstance(line, int) and line >= 1 for line in entry["source_lines"])
            and entry["source_lines"] == sorted(set(entry["source_lines"]))
            for entry in entries
        ))
        self.assertTrue(all(entry["review_status"] == "pending_native_review" for entry in entries))

        source = HTML
        # Skip one JavaScript normalization function whose regex literals contain
        # quote characters; its Arabic user-facing errors are asserted in catalog.
        numeric_start = source.index("const egpToPiasters=raw=>{")
        numeric_end = source.index("\n};", numeric_start) + 3
        source = source[:numeric_start] + source[numeric_end:]
        for message in ("تحقق من فواصل الآلاف في المبلغ", "أدخل مبلغاً صحيحاً حتى قرشين عشريين", "المبلغ خارج النطاق المسموح"):
            self.assertIn(message, reviewed)
        found = set()
        index = 0
        while index < len(source):
            quote = source[index]
            if quote not in ("'", '"', "`"):
                index += 1
                continue
            index += 1
            value = []
            while index < len(source):
                char = source[index]
                if char == "\\":
                    value.append(char)
                    if index + 1 < len(source):
                        value.append(source[index + 1])
                        index += 2
                    else:
                        index += 1
                    continue
                if char == quote:
                    index += 1
                    break
                value.append(char)
                index += 1
            literal = "".join(value).strip()
            # This lightweight scanner is not a JavaScript lexer: regex literals
            # containing quote characters can otherwise be mistaken for UI copy.
            if literal.startswith(").replace(/") or literal.startswith(").trim().replace(/[٠-٩۰-۹]"):
                continue
            if re.search(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]", literal) and literal:
                found.add(literal)

        markup = re.sub(r"<script[^>]*>.*?</script>|<style[^>]*>.*?</style>", "", source, flags=re.S)
        for node in re.findall(r">([^<>]+)<", markup):
            node = node.strip()
            if re.search(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]", node) and node:
                found.add(node)
        missing = sorted(found - reviewed)
        self.assertEqual(missing, [], "Arabic UI literals missing from static/ar-ui-review.json")

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

    def test_primary_navigation_uses_native_buttons_and_announces_current_page(self):
        self.assertIn("h('button',{type:'button',className:PAGE===id?'on':'','aria-current':PAGE===id?'page':null", HTML)
        self.assertNotIn("role:'button',tabIndex:0,'aria-current':PAGE===id?'page':null", HTML)
        self.assertIn("#side .primary-nav button:focus-visible", HTML)
        self.assertIn("#side .primary-nav button.on", HTML)

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
        self.assertIn("uiText('PDF وDOCX فقط · 15 ميجابايت كحد أقصى لكل ملف','PDF and DOCX only · 15 MB maximum per file')", HTML)

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

    def test_admin_deadline_holiday_editor_is_available(self):
        self.assertIn("api('/deadline-holidays')", HTML)
        self.assertIn("api('/deadline-holidays','PUT'", HTML)
        self.assertIn("ME.role==='admin'", HTML)


    def test_phone_layout_keeps_body_copy_and_tap_targets_readable(self):
        self.assertIn("button{min-height:44px}", HTML)
        self.assertIn(".research-role,.research-sources-title,.research-pin,#main .quick-link span,#main .workspace-list-item .item-meta,.research-controls label,.research-source-actions button,.research-message-actions button,#side .me,#side .me a,.pill{font-size:14px}", HTML)
        self.assertIn("@media(max-width:420px){body{font-size:15px}", HTML)
        self.assertIn(".auth-card form>label{display:block;width:100%", HTML)
        self.assertIn(".auth-card .password-row input{min-width:0;flex:1}", HTML)


    def test_whatsapp_reminder_handoff_uses_explicit_click_and_encoded_wa_me_url(self):
        self.assertIn("const whatsappReminder=(dueDate,kind)=>", HTML)
        self.assertIn("window.prompt(", HTML)
        self.assertIn("https://wa.me/", HTML)
        self.assertIn("encodeURIComponent(message)", HTML)
        self.assertIn("whatsappReminder(s.date,'session')", HTML)
        self.assertIn("whatsappReminder(d.due,'deadline')", HTML)
        self.assertIn("Please confirm the details with the law office.", HTML)

    def test_reminder_preferences_screen_exposes_per_user_schedule_controls(self):
        self.assertIn("api('/reminder-preferences')", HTML)
        self.assertIn("api('/reminder-preferences','PUT',payload)", HTML)
        for key in ("email_enabled", "deadline_7_days", "deadline_3_days",
                    "deadline_1_day", "deadline_day_of", "deadline_overdue",
                    "session_day_of", "task_reminders"):
            self.assertIn("['" + key + "'", HTML)
        self.assertIn("تُطبق هذه الخيارات على حسابك داخل هذا المكتب فقط", HTML)


    def test_deadline_calculation_can_be_saved_with_visible_audit_note(self):
        self.assertIn("const calculationNote=", HTML)
        self.assertIn("const saveCalculated=btn(", HTML)
        self.assertIn("Save calculated deadline to case", HTML)
        self.assertIn("await api('/cases/'+id+'/deadlines','POST'", HTML)
        self.assertIn("Calculation steps", HTML)
        self.assertIn("Warnings", HTML)



    def test_mobile_navigation_hint_typography_and_touch_targets(self):
        self.assertIn("className:'nav-scroll-hint'", HTML)
        self.assertIn("Swipe for more", HTML)
        self.assertIn("#side a[role=button]{min-height:44px}", HTML)
        self.assertIn(".tabs a{min-height:44px", HTML)
        self.assertIn("font-size:14px", HTML)
        self.assertIn("@media(max-width:420px)", HTML)
        self.assertIn("Request an account", HTML)



    def test_subscription_billing_ui_has_trial_transfer_and_operator_review(self):
        self.assertIn("api('/billing')", HTML)
        self.assertIn("api('/billing/subscribe','POST'", HTML)
        self.assertIn("api('/billing/payment-submissions','POST'", HTML)
        self.assertIn("api('/platform/billing/payment-submissions')", HTML)
        self.assertIn("bank_transfer", HTML)
        self.assertIn("instapay", HTML)
        self.assertIn("platformBillingPage", HTML)


    def test_answer_correction_button_and_trust_tier_badges_are_rendered(self):
        self.assertIn("Suggest a correction", HTML)
        self.assertIn("api('/answers/corrections','POST'", HTML)
        self.assertIn("api('/admin/corrections')", HTML)
        self.assertIn("trustTierBadge", HTML)
        self.assertIn("Source-matched — not verified", HTML)
        self.assertIn("Unreviewed", HTML)
        self.assertIn("Verified", HTML)

    def test_case_notes_surface_safe_arabic_drafting_skeletons(self):
        self.assertIn("/draft-skeleton?document_type=", HTML)
        self.assertIn("Generate memo skeleton", HTML)
        self.assertIn("Generate pleading skeleton", HTML)
        self.assertIn("Heading-only templates", HTML)
        self.assertIn("محامٍ", HTML)

    def test_case_invoice_and_finance_screens_use_integer_piasters(self):
        self.assertIn("['invoices',uiText('الفواتير','Invoices')]", HTML)
        self.assertIn("['finance',navLabel('الفواتير والتحصيل','Invoices & Finance'),financePage]", HTML)
        self.assertIn("const toPiasters=value=>", HTML)
        self.assertIn("const toMilli=value=>", HTML)
        self.assertIn("api('/cases/'+id+'/invoices','POST'", HTML)
        self.assertIn("api('/invoices/'+item.id+'/issue','POST')", HTML)
        self.assertIn("api('/invoices/'+item.id+'/payments','POST'", HTML)
        self.assertIn("api('/finance/invoices/overview')", HTML)
        self.assertIn("/payments/'+payment.id+'/receipt", HTML)
        self.assertIn("not an Egyptian e-tax invoice", HTML)
        self.assertIn("api('/invoices/'+item.id+'/void','POST'", HTML)

    def test_invoice_and_subscription_amounts_share_arabic_piaster_parser(self):
        self.assertIn("const egpToPiasters=raw=>", HTML)
        self.assertIn("const toPiasters=value=>egpToPiasters(value)", HTML)
        self.assertIn("piasters=egpToPiasters(amount.value)", HTML)
        self.assertIn(r".replace(/[٠-٩۰-۹]/g", HTML)
        self.assertIn(".replace(/٫/g,'.').replace(/٬/g,',')", HTML)
        self.assertIn("Check the amount thousands separators", HTML)
        self.assertIn("Number(parts[0])*100", HTML)


    def test_calendar_supports_today_and_monday_to_sunday_week_filters(self):
        self.assertIn("new Option(uiText('اليوم','Today'),'today')", HTML)
        self.assertIn("new Option(uiText('هذا الأسبوع','This week'),'week')", HTML)
        self.assertIn("weekStart.setDate(weekStart.getDate()-((weekStart.getDay()+6)%7))", HTML)
        self.assertIn("weekEnd.setDate(weekEnd.getDate()+6)", HTML)
        self.assertIn("range.onchange=draw", HTML)
        self.assertIn("itemDay(x)<weekStartKey||itemDay(x)>weekEndKey", HTML)


    def test_document_review_disclosure_exposes_controlled_expanded_state(self):
        self.assertIn("id:'doc-review-'+id+'-'+d.document_id", HTML)
        self.assertIn("toggle.setAttribute('aria-controls',reviewPanel.id)", HTML)
        self.assertIn("toggle.setAttribute('aria-expanded','false')", HTML)
        self.assertIn("toggle.setAttribute('aria-expanded','true')", HTML)
        self.assertIn("toggle.setAttribute('aria-expanded','false');reviewPanel.replaceChildren()", HTML)

    def test_document_review_loading_and_completion_states_are_announced(self):
        self.assertIn("role:'status','aria-live':'polite'", HTML)
        self.assertIn("role:'status','aria-live':'polite',textContent:uiText('جارٍ تحميل المقاطع…','Loading text chunks…')", HTML)
        self.assertIn("Loaded '+chunkCount+' text chunks for review", HTML)
        self.assertIn("تم تحميل '+chunkCount+' مقطعاً للمراجعة", HTML)


    def test_browser_acceptance_installs_and_runs_pinned_axe_wcag_gate(self):
        workflow = (ROOT / ".github" / "workflows" / "browser-e2e.yml").read_text(encoding="utf-8")
        browser_tests = (ROOT / "tests" / "browser" / "test_acceptance.py").read_text(encoding="utf-8")
        self.assertIn("axe-core@4.10.3", workflow)
        self.assertIn("uses: actions/setup-node@v6", workflow)
        self.assertIn("axe.min.js", browser_tests)
        self.assertIn("self.page.route(", browser_tests)
        self.assertIn("self.page.add_script_tag(url=\"/__axe__/axe.min.js\")", browser_tests)
        self.assertIn("name=nav_name, exact=True", browser_tests)
        self.assertIn("name=\"المهام\", exact=True", browser_tests)
        self.assertIn("'wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'", browser_tests)
        self.assertIn("test_axe_wcag_accessibility_smoke_arabic_english_and_mobile", browser_tests)
        self.assertIn("((1440, 900), (768, 900), (640, 900), (390, 844), (320, 720))", browser_tests)
        self.assertIn('self.page.set_viewport_size({"width": 390, "height": 844})', browser_tests)
        self.assertIn("Horizontal page overflow at", browser_tests)
        self.assertIn("document.documentElement.scrollWidth <= window.innerWidth + 1", browser_tests)


    def test_dynamic_form_label_siblings_are_programmatically_associated(self):
        self.assertIn("let generatedControlId=0", HTML)
        self.assertIn("label.tagName==='LABEL'&&!label.htmlFor", HTML)
        self.assertIn("/^(INPUT|SELECT|TEXTAREA)$/.test(control.tagName)", HTML)
        self.assertIn("label.htmlFor=control.id", HTML)
        self.assertIn("p.placeholder&&!e.hasAttribute('aria-label')", HTML)


    def test_workspace_filters_and_feedback_selects_have_accessible_names(self):
        for label in (
            "Filter tasks by status",
            "Filter calendar by type",
            "Filter calendar by date",
            "Filter cases by status",
            "Feedback category",
            "Invited user role",
        ):
            self.assertIn(label, HTML)


    def test_dynamic_casework_billing_and_legal_review_selects_are_named(self):
        for label in (
            "Selected subscription plan",
            "Payment method",
            "Legal version",
            "Review type",
            "Review outcome",
            "Task assignee",
            "Task due date",
            "Hearing date",
            "Deadline calculation rule",
            "Deadline trigger date",
            "Additional days",
            "Team member",
            "Case member role",
        ):
            self.assertIn(label, HTML)


    def test_case_consent_and_document_upload_controls_have_accessible_names(self):
        self.assertIn("Confirm firm authorization to process matter data", HTML)
        self.assertIn("Confirm client consent to process matter data", HTML)
        self.assertIn("Choose a case document in PDF or Word format", HTML)


    def test_ai_brief_and_deadline_async_states_are_announced(self):
        self.assertIn("Preparing a brief from case records...", HTML)
        self.assertIn("role:'status','aria-live':'polite','aria-atomic':'true',textContent:uiText('جارٍ إعداد الملخص", HTML)
        self.assertIn("role:'alert','aria-live':'assertive'", HTML)
        self.assertIn("Brief generation completed", HTML)
        self.assertIn("A preliminary deadline has been calculated", HTML)
        self.assertIn("catch(e){preview.replaceChildren(h('p',{className:'bad',role:'alert'", HTML)
        self.assertIn("role:'status','aria-live':'polite','aria-atomic':'true',textContent:uiText('جارٍ الحساب...','Calculating...')", HTML)


    def test_primary_navigation_inactive_and_hover_colors_keep_dark_sidebar_contrast(self):
        self.assertIn("background:transparent;color:#c9d4e8", HTML)
        self.assertIn("color:#c9d4e8;text-align:start", HTML)
        self.assertIn("background:#243b66;color:#fff", HTML)
        self.assertIn("background:var(--ui-blue-soft);color:var(--ui-blue)", HTML)


    def test_success_pill_text_uses_contrast_safe_green_token(self):
        self.assertIn("--ok:#166534;--ok-l:#E7F6EC", HTML)
        self.assertIn("--ok:#166534;--ok-l:#E8F7EF", HTML)
        self.assertIn("--mut:#5F6B7C", HTML)
        self.assertIn("--ui-muted: #596579;", HTML)
        self.assertNotIn("--ok:#15803D;--ok-l:#E7F6EC", HTML)


    def test_native_navigation_keeps_horizontal_mobile_and_forced_color_support(self):
        self.assertIn("#side .primary-nav button { width:auto; min-width:max-content; flex:0 0 auto; white-space:nowrap; }", HTML)
        self.assertIn("#side nav button.on { border: 1px solid Highlight; }", HTML)


    def test_form_controls_have_high_contrast_boundaries_and_focus_rings(self):
        self.assertIn("--ui-control-border: #8292a8;", HTML)
        self.assertIn("input,select,textarea{border-color:var(--ui-control-border);min-height:40px}", HTML)
        self.assertIn("--ui-control-hover: #7c8da3;", HTML)
        self.assertIn("outline: 3px solid var(--ui-focus-ring);", HTML)
        self.assertIn("input:focus-visible,select:focus-visible,textarea:focus-visible,button:focus-visible,a:focus-visible{outline:3px solid #2457C5", HTML)
        self.assertNotIn("outline:3px solid #2457C533", HTML)


    def test_browser_suite_checks_native_navigation_space_and_enter(self):
        browser_tests = (ROOT / "tests" / "browser" / "test_acceptance.py").read_text(encoding="utf-8")
        self.assertIn("test_primary_navigation_buttons_support_native_keyboard_activation", browser_tests)
        self.assertIn('self.page.keyboard.press("Space")', browser_tests)
        self.assertIn('self.page.keyboard.press("Enter")', browser_tests)


    def test_live_toast_is_mobile_safe_and_does_not_clip_long_messages(self):
        toast = HTML[HTML.index("#toast{"):HTML.index("\\n", HTML.index("#toast{"))]
        self.assertIn("z-index:10000", toast)
        self.assertIn("env(safe-area-inset-bottom,0px)", toast)
        self.assertIn("max-width:min(32rem,calc(100vw - 32px))", toast)
        self.assertIn("white-space:normal", toast)
        self.assertIn("overflow-wrap:anywhere", toast)


    def test_browser_modal_acceptance_checks_focus_wrap_escape_and_return(self):
        browser_tests = (ROOT / "tests" / "browser" / "test_acceptance.py").read_text(encoding="utf-8")
        self.assertIn('self.page.keyboard.press("Tab")', browser_tests)
        self.assertIn('self.page.keyboard.press("Escape")', browser_tests)
        self.assertIn('dialog.locator("input").first.evaluate("(el) => el === document.activeElement")', browser_tests)
        self.assertIn('new_case_opener.evaluate("(el) => el === document.activeElement")', browser_tests)


    def test_css_custom_properties_are_defined_before_use(self):
        referenced = set(re.findall(r"var\(--([a-zA-Z0-9_-]+)", HTML))
        defined = set(re.findall(r"--([a-zA-Z0-9_-]+)\s*:", HTML))
        self.assertEqual(referenced - defined, set(), "Undefined CSS custom properties")


    def test_case_task_session_deadline_and_payment_fields_have_explicit_names(self):
        for label in (
            "New task title",
            "Hearing details",
            "Deadline type",
            "Deadline due date",
            "Deadline notes",
            "Payment amount in EGP",
            "Transfer reference (optional)",
            "Fee due date",
        ):
            self.assertIn(label, HTML)


    def test_select_date_and_file_controls_do_not_use_unnamed_constructors(self):
        self.assertNotIn("h('select',{})", HTML)
        self.assertNotIn("h('input',{type:'date'})", HTML)
        self.assertIn("type:'file',accept:'.csv,text/csv','aria-label'", HTML)
        self.assertIn("type:'file',accept:'.pdf,.docx','aria-label'", HTML)


    def test_modal_dialogs_inert_background_and_restore_it_on_close(self):
        self.assertIn("const shell=$('shell');if(shell)shell.inert=true;A.append(overlay)", HTML)
        self.assertIn("if(shell&&!document.querySelector('.modal-backdrop'))shell.inert=false", HTML)
        self.assertIn("overlay.remove()", HTML)


    def test_new_case_validation_error_is_associated_and_clears_on_input(self):
        self.assertIn("id:'new-case-title-error',className:'bad',role:'alert',hidden:true", HTML)
        self.assertIn("k==='title'?titleError:null", HTML)
        self.assertIn("inputs.title.setAttribute('aria-describedby',titleError.id)", HTML)
        self.assertIn("inputs.title.addEventListener('invalid'", HTML)
        self.assertIn("inputs.title.setAttribute('aria-invalid','true')", HTML)
        self.assertIn("inputs.title.removeAttribute('aria-invalid');titleError.hidden=true", HTML)


    def test_modal_accessible_names_reference_visible_headings(self):
        self.assertIn("'aria-labelledby':'new-case-title'", HTML)
        self.assertIn("id:'new-case-title'", HTML)
        self.assertIn("'aria-labelledby':'client-profile-title'", HTML)
        self.assertIn("id:'client-profile-title'", HTML)

    def test_browser_modal_checks_required_title_error_and_recovery(self):
        browser_tests = (ROOT / "tests" / "browser" / "test_acceptance.py").read_text(encoding="utf-8")
        self.assertIn('title_field.get_attribute("aria-invalid")', browser_tests)
        self.assertIn('title_field.get_attribute("aria-describedby")', browser_tests)
        self.assertIn('dialog.get_by_role("alert").is_visible()', browser_tests)
        self.assertIn('title_field.fill("Synthetic accessibility case")', browser_tests)


    def test_login_validation_errors_are_associated_and_announced(self):
        self.assertIn("id:'login-form-error',className:'bad',role:'alert',hidden:true", HTML)
        self.assertIn("e.setAttribute('aria-describedby',loginError.id);p.setAttribute('aria-describedby',loginError.id)", HTML)
        self.assertIn("field.addEventListener('invalid'", HTML)
        self.assertIn("e.setAttribute('aria-invalid','true')", HTML)
        self.assertIn("p.setAttribute('aria-invalid','true')", HTML)
        self.assertIn("loginError.hidden=false", HTML)


    def test_browser_login_validation_error_and_recovery_are_exercised(self):
        browser_tests = (ROOT / "tests" / "browser" / "test_acceptance.py").read_text(encoding="utf-8")
        self.assertIn("test_login_form_exposes_and_clears_associated_validation_errors", browser_tests)
        self.assertIn('email.get_attribute("aria-describedby")', browser_tests)
        self.assertIn('password.get_attribute("aria-invalid")', browser_tests)
        self.assertIn('email.fill("synthetic@example.test")', browser_tests)


    def test_login_validation_alert_hidden_attribute_is_not_overridden_by_inline_display(self):
        self.assertIn("role:'alert',hidden:true", HTML)
        self.assertNotIn("role:'alert',hidden:true,style:'display:block'", HTML)
        self.assertIn("loginError.hidden=true", HTML)


    def test_case_title_validation_alert_uses_associated_hidden_state(self):
        self.assertIn("inputs.title.setAttribute('aria-describedby',titleError.id)", HTML)
        self.assertIn("inputs.title.addEventListener('invalid'", HTML)
        self.assertIn("titleError.hidden=false", HTML)
        self.assertIn("titleError.hidden=true", HTML)
        self.assertNotIn("id:'new-case-title-error',className:'bad',role:'alert',hidden:true,style:'display:block'", HTML)


    def test_dashboard_exposes_active_matter_shortlist_and_respects_accessible_case_list(self):
        self.assertIn("className:'card workspace-active-cases'", HTML)
        self.assertIn("active.slice(0,5).map(c=>listItem", HTML)
        self.assertIn("()=>view(c.id)", HTML)
        self.assertIn("active.length", HTML)

    def test_legal_research_uses_three_pane_source_inspector_without_changing_evidence_contract(self):
        self.assertIn("className:'research-inspector card'", HTML)
        self.assertIn("role:'region',tabIndex:0,'aria-label':LANG==='ar'?'فحص المصدر':'Source inspector'", HTML)
        self.assertIn("grid-template-columns:minmax(205px,235px) minmax(0,1fr) minmax(260px,310px)", HTML)
        self.assertIn("id:'research-source-inspector'", HTML)
        self.assertIn("id:'research-history-pane'", HTML)
        self.assertIn("'aria-controls':'research-history-pane'", HTML)
        self.assertIn("sidebar.classList.toggle('history-collapsed')", HTML)
        self.assertIn(".research-list.history-collapsed>:not(.research-list-head){display:none!important}", HTML)
        self.assertIn("'aria-controls':'research-source-inspector'", HTML)
        self.assertIn("'aria-expanded':'false'", HTML)
        self.assertIn("trigger.setAttribute('aria-expanded','true')", HTML)
        self.assertIn("returnTo.setAttribute('aria-expanded','false')", HTML)
        self.assertIn("className:'g research-inspect-action'", HTML)
        self.assertIn("onclick:e=>inspectSource(s,status,pin,p,e.currentTarget)", HTML)
        self.assertIn("source.text|| (LANG==='ar'?'لم يُرجع نص لهذا السجل من المصدر.':'No passage text was returned for this source record.')", HTML)
        self.assertIn("review_evidence", HTML)
        self.assertIn("const latestByType=Object.create(null)", HTML)
        self.assertIn("const latestReviews=Object.values(latestByType)", HTML)
        self.assertIn("const resetInspector=(returnFocus=false)=>", HTML)
        self.assertIn("sourceInspector.__focusReturn=trigger||document.activeElement", HTML)
        self.assertIn("onclick:()=>resetInspector(true)", HTML)
        self.assertIn("onkeydown:e=>{if(e.key==='Escape'&&sourceInspector.__focusReturn)", HTML)
        self.assertIn("sourceInspector.focus({preventScroll:true})", HTML)
        self.assertIn("@media(max-width:1120px)", HTML)
        self.assertIn("@media(max-width:800px)", HTML)
        self.assertIn(".research-layout>.research-list{max-height:210px;overflow:auto}", HTML)
        self.assertIn(".research-layout>.research-inspector{max-height:380px;overflow:auto}", HTML)
        self.assertIn("@media(prefers-reduced-motion:reduce){#main .quick-link{transition:none}#main .quick-link:hover{transform:none}}", HTML)


    def test_language_switch_preserves_first_run_and_setup_health_views(self):
        self.assertIn("else if(PAGE==='setup')firstRunPage();else if(PAGE==='setup-health')setupHealthPage();", HTML)


    def test_inspecting_a_second_source_closes_the_previous_expanded_control(self):
        self.assertIn("const previousTrigger=sourceInspector.__focusReturn", HTML)
        self.assertIn("previousTrigger!==trigger&&previousTrigger.isConnected", HTML)
        self.assertIn("previousTrigger.setAttribute('aria-expanded','false')", HTML)


    def test_source_inspector_preserves_document_page_and_confidence_provenance(self):
        self.assertIn("p.original_document_name||p.document_name||source.original_document_name||source.document_name||source.file_name", HTML)
        self.assertIn("source.page_number??p.page_number", HTML)
        self.assertIn("source.text_location||p.text_location||source.location||p.location", HTML)
        self.assertIn("source.confidence??p.confidence", HTML)
        self.assertIn("(typeof confidence==='number'||typeof confidence==='string')&&confidence!==''", HTML)
        self.assertIn("Original document: ", HTML)
        self.assertIn("Page: ", HTML)
        self.assertIn("Recorded confidence: ", HTML)


    def test_subscription_lock_routes_admins_to_billing_and_informs_members(self):
        self.assertIn("if(ME.role==='admin')billingPage().catch(()=>{});else toast(LANG==='ar'?'المكتب في وضع القراءة فقط؛ تواصل مع مسؤول المكتب.':'This firm is in read-only mode; contact your firm administrator.')", HTML)
        self.assertIn("!p.startsWith('/account/mfa/')", HTML)



    def test_mobile_body_text_and_login_layout_remain_legible_at_phone_width(self):
        self.assertIn("@media(max-width:420px){body{font-size:15px}", HTML)
        self.assertIn(".auth-card{width:calc(100% - 20px);margin:4vh auto;padding:16px}", HTML)
        self.assertIn(".auth-card .password-row{display:flex;width:100%;min-width:0;align-items:stretch}", HTML)
        self.assertIn(".auth-card .password-row input{min-width:0;flex:1}", HTML)
        self.assertIn(".auth-card .password-row button{min-height:44px;flex:0 0 auto}", HTML)


    def test_document_intelligence_workspace_is_matter_scoped_and_bounded(self):
        self.assertIn("function documentIntelligencePanel(caseId,documents)", HTML)
        self.assertIn("api('/cases/'+caseId+'/docs/'+doc.document_id+'/chunks')", HTML)
        self.assertIn("for(const doc of docs.slice(0,40))", HTML)
        self.assertIn("if(totalChars+text.length>1000000)", HTML)
        self.assertIn("data.intelligence.classification", HTML)
        self.assertIn("item.intelligence.candidates", HTML)
        self.assertIn("server_document_intelligence_unavailable", HTML)
        self.assertIn("openDocumentWorkspace=makeBtn", HTML)
        self.assertIn("documentWorkspace.replaceChildren(documentIntelligencePanel", HTML)
        self.assertIn("const needle=normalize(query.value.trim())", HTML)

    def test_document_intelligence_candidates_keep_provenance_and_unverified_status(self):
        self.assertIn("item.intelligence.candidates", HTML)
        self.assertIn("candidate.chunk_ref", HTML)
        self.assertIn("candidate.page", HTML)
        self.assertIn("Candidate output was capped", HTML)
        self.assertNotIn("const extractCandidates=", HTML)
        self.assertNotIn("const classify=(filename,text)=>", HTML)
        self.assertIn("No deadlines are created automatically.", HTML)
        self.assertIn("No text differences were reported between the two versions.", HTML)

    def test_cross_document_comparison_uses_authorized_provenance_api_and_literal_hunks(self):
        panel = HTML[HTML.index("function documentIntelligencePanel(caseId,documents)"):HTML.index("async function view(id)")]
        self.assertIn("api('/documents/compare?'+params.toString())", panel)
        self.assertIn("before_document_id", panel)
        self.assertIn("after_document_id", panel)
        self.assertIn("result.before?.sources", panel)
        self.assertIn("result.after?.sources", panel)
        self.assertIn("Requires lawyer review", panel)
        self.assertIn("Literal text comparison only", panel)
        self.assertIn("String(change.before||", panel)
        self.assertIn("String(change.after||", panel)

    def test_structured_entity_event_and_relationship_candidates_render_with_provenance(self):
        panel = HTML[HTML.index("function documentIntelligencePanel(caseId,documents)"):HTML.index("async function view(id)")]
        self.assertIn("item.intelligence.structured", panel)
        self.assertIn("allStructured.entities", panel)
        self.assertIn("allStructured.events", panel)
        self.assertIn("allStructured.relationships", panel)
        self.assertIn("record.page", panel)
        self.assertIn("record.chunk_ref", panel)
        self.assertIn("dates and parties only when they appear in the same sentence", panel)
        self.assertIn("No explicit relationship candidates were found.", panel)

    def test_matter_wide_timeline_uses_server_provenance_and_review_warnings(self):
        panel = HTML[HTML.index("function documentIntelligencePanel(caseId,documents)"):HTML.index("async function view(id)")]
        self.assertIn("api('/cases/'+caseId+'/documents/timeline')", panel)
        self.assertIn("result.dated_mentions", panel)
        self.assertIn("result.unparsed_mentions", panel)
        self.assertIn("result.event_candidates", panel)
        self.assertIn("item.chunk_ref", panel)
        self.assertIn("result.warning", panel)
        self.assertIn("No date or event mentions were found in accessible documents.", panel)

    def test_document_classification_edits_are_persisted_with_audit_and_version_checks(self):
        self.assertIn("draftOverrides", HTML)
        self.assertIn("Save classification", HTML)
        self.assertIn("classification','PUT'", HTML)
        self.assertIn("expected_version:persisted?persisted.version:0", HTML)
        self.assertIn("Classification change history", HTML)

    def test_document_original_download_uses_existing_audited_route(self):
        self.assertIn("/cases/'+id+'/docs/'+d.document_id+'/original", HTML)
        self.assertIn("credentials:'same-origin'", HTML)
        self.assertIn("Download original (if retained)", HTML)

    def test_document_duplicate_signals_are_limited_to_current_matter(self):
        self.assertIn("byte_identical_candidate", HTML)
        self.assertIn("text_identical_extraction_candidate", HTML)
        self.assertIn("Review signals within this matter only", HTML)
        self.assertIn("text equality does not prove original-file identity", HTML)


    def test_research_document_upload_is_matter_scoped_and_explicit(self):
        self.assertIn("accept:'.pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document'", HTML)
        self.assertIn("multiple:true", HTML)
        self.assertIn("encodeURIComponent(matterSelect.value)+'/upload'", HTML)
        self.assertIn("uploadSubmit=makeBtn", HTML)
        self.assertIn("uploadInput.onchange=()=>{const count=uploadInput.files?.length||0;uploadSubmit.disabled=!matterSelect.value||!count", HTML)
        self.assertIn("item.file.size<=15000000", HTML)
        self.assertIn("credentials:'same-origin'", HTML)
        self.assertIn("X-CSRF-Token", HTML)
        self.assertIn("result.original_file_retained===false", HTML)

    def test_research_upload_warnings_distinguish_ocr_partial_and_failure(self):
        self.assertIn("if(result.ocr_used)", HTML)
        self.assertIn("if(result.ocr_warning)", HTML)
        self.assertIn("OCR was used. Extracted text is unverified", HTML)
        self.assertIn("Only readable pages were indexed", HTML)
        self.assertIn("No readable text could be extracted", HTML)
        self.assertIn(".notice.warning{", HTML)
        self.assertIn(".notice.danger{", HTML)

    def test_research_workspace_uses_coherent_light_palette_and_responsive_upload_layout(self):
        self.assertIn("--workspace-ink:#17243a", HTML)
        self.assertIn("--workspace-blue:#2457c5", HTML)
        self.assertIn("--workspace-success:#176b45", HTML)
        self.assertIn("--workspace-warning:#8a4b08", HTML)
        self.assertIn("--workspace-danger:#a52620", HTML)
        self.assertIn("@media(max-width:800px){#main .research-controls{grid-template-columns:minmax(0,1fr)}", HTML)
        self.assertIn(".research-upload-panel{grid-template-columns:minmax(0,1fr)}", HTML)


    def test_application_color_tokens_resolve_to_one_light_palette(self):
        self.assertIn("--navy:#14284b;--bg:#f5f7fb;--line:#dbe3ee", HTML)
        self.assertIn("--pri:#2457c5;--pri-l:#edf3ff;--ok:#176b45", HTML)
        self.assertIn("--warn:#8a4b08;--warn-l:#fff5e8;--bad:#a52620", HTML)
        self.assertIn("--ui-blue:#2457c5;--ui-blue-soft:#edf3ff", HTML)
        self.assertIn("--ui-border:#dbe3ee;--ui-muted:#5b6b80", HTML)


    def test_legal_source_warning_is_prominent_without_promoting_verification(self):
        self.assertIn("className:'research-source-caution '+(status==='verified_operative_text'?'verified':'warning')", HTML)
        self.assertIn("statusDescriptions[status]||statusDescriptions.outdated_or_under_review", HTML)
        self.assertIn(".research-source-caution.warning{", HTML)
        self.assertIn(".research-source-caution.verified{", HTML)
        self.assertIn(".research-source-caution.verified{background:var(--workspace-success-bg)", HTML)
        self.assertIn("border-inline-start:3px solid var(--workspace-success)", HTML)



    def test_figma_legal_research_refresh_preserves_three_pane_and_upload_workflows(self):
        self.assertIn("--figma-navy:#071b31", HTML)
        self.assertIn("#side{background:#071b31;color:#e7edf6", HTML)
        self.assertIn("#side a.on,#side a:hover{background:#1b3554;color:#fff}", HTML)

        def luminance(color):
            channels = [int(color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
            linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in channels]
            return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]

        def contrast(first, second):
            values = sorted((luminance(first), luminance(second)), reverse=True)
            return (values[0] + 0.05) / (values[1] + 0.05)

        self.assertGreaterEqual(contrast("#cbd6e5", "#071b31"), 7.0)
        self.assertGreaterEqual(contrast("#ffffff", "#1b3554"), 7.0)
        self.assertGreaterEqual(contrast("#ffffff", "#2457c5"), 4.5)
        self.assertGreaterEqual(contrast("#A95B08", "#FFF4E4"), 4.5)
        self.assertGreaterEqual(contrast("#166534", "#E8F7EF"), 4.5)
        self.assertGreaterEqual(contrast("#B42318", "#FDECEC"), 4.5)
        self.assertGreaterEqual(contrast("#8a4b08", "#fff5e8"), 4.5)
        self.assertGreaterEqual(contrast("#176b45", "#e8f7ef"), 4.5)
        self.assertGreaterEqual(contrast("#a52620", "#fdecec"), 4.5)
        self.assertGreaterEqual(contrast("#2457c5", "#edf3ff"), 4.5)
        self.assertIn("#main .research-layout{grid-template-columns:minmax(210px,245px) minmax(0,1fr) minmax(250px,300px)", HTML)
        self.assertIn("#main .research-composer{order:1", HTML)
        self.assertIn("#main .research-thread{order:2", HTML)
        self.assertIn("#main #research-source-inspector", HTML)
        self.assertIn("uploadFiles=async files=>", HTML)
        self.assertIn("const documentWorkspace=h('div',{})", HTML)

    def test_figma_research_refresh_keeps_accessible_responsive_controls(self):
        self.assertIn("@media(max-width:800px){#side{background:var(--figma-navy)", HTML)
        self.assertIn("#main .research-composer button{width:100%}", HTML)
        self.assertIn("@media(prefers-reduced-motion:reduce){#main *", HTML)
        self.assertIn("role:'region',tabIndex:0", HTML)

    def test_document_upload_dropzone_supports_keyboard_and_drag_feedback(self):
        self.assertIn("role:'button',tabIndex:0", HTML)
        self.assertIn("press Enter or Space to choose files", HTML)
        self.assertIn("if(e.key==='Enter'||e.key===' ')", HTML)
        self.assertIn("e.currentTarget.classList.add('is-dragover')", HTML)
        self.assertIn("e.currentTarget.classList.remove('is-dragover')", HTML)
        self.assertIn(".research-upload-dropzone:focus-visible", HTML)

    def test_document_intelligence_exposes_audited_extraction_review_actions(self):
        self.assertIn("const renderChunkReviewCards=()=>{", HTML)
        self.assertIn("renderChunkReviewCards()", HTML)
        self.assertIn("'/cases/'+caseId+'/docs/'+item.doc.document_id+'/chunks/'+chunk.id+'/review'", HTML)
        self.assertIn("outcome:'accepted'", HTML) if "outcome:'accepted'" in HTML else self.assertIn("submitChunkReview(item,chunk,'accepted'", HTML)
        self.assertIn("submitChunkReview(item,chunk,'needs_recheck'", HTML)
        self.assertIn("submitChunkReview(item,chunk,'corrected'", HTML)
        self.assertIn("payload.expected_text_sha256=chunk.text_sha256", HTML)
        self.assertIn("item.chunks=Array.isArray(refreshed.chunks)?refreshed.chunks:[]", HTML)
        self.assertIn("first 100 chunks", HTML)
        self.assertIn("latest_review", HTML)

    def test_extraction_review_arabic_copy_is_registered(self):
        catalog = json.loads((ROOT / "static" / "ar-ui-review.json").read_text(encoding="utf-8"))
        self.assertEqual(catalog["entry_count"], len(catalog["entries"]))
        reviewed = {entry["arabic"] for entry in catalog["entries"]}
        self.assertIn("اعتماد النص", reviewed)
        self.assertIn("حفظ قرار مراجعة الاستخراج في سجل التدقيق.", reviewed)

    def test_documents_page_is_a_matter_scoped_library_not_a_fabricated_firm_wide_index(self):
        self.assertIn("['documents',navLabel('المستندات','Documents'),documentsPage]", HTML)
        page = HTML[HTML.index("async function documentsPage(){"):HTML.index("\nasync function law(){")]
        self.assertIn("cases/search?", page)
        self.assertIn("await api('/cases/'+id)", page)
        self.assertIn("documentIntelligencePanel(id,docs)", page)
        self.assertIn("window.DOCUMENT_MATTER_ID=id", page)
        self.assertIn("Upload and index files", page)
        self.assertNotIn("firm-wide document count", page.lower())

    def test_extraction_review_ui_uses_audited_api_and_bounded_history(self):
        self.assertIn("const renderChunkReviewCards=()=>{", HTML)
        self.assertIn("submitChunkReview(item,chunk,'accepted'", HTML)
        self.assertIn("submitChunkReview(item,chunk,'needs_recheck'", HTML)
        self.assertIn("submitChunkReview(item,chunk,'corrected'", HTML)
        self.assertIn("payload.expected_text_sha256=chunk.text_sha256", HTML)
        self.assertIn("'/cases/'+caseId+'/docs/'+item.doc.document_id+'/reviews'", HTML)
        self.assertIn("records.slice(0,100)", HTML)
        self.assertIn("if(records.length>=100)break", HTML)
        self.assertIn("review.reviewed_text", HTML)

    def test_document_library_displays_real_matter_document_metadata(self):
        page = HTML[HTML.index("async function documentsPage(){"):HTML.index("\nasync function law(){")]
        self.assertIn("doc.content_type", page)
        self.assertIn("doc.added", page)
        self.assertIn("doc.byte_size", page)
        self.assertIn("doc.extraction_status", page)
        self.assertIn("doc.ocr_used", page)

    def test_document_library_clears_stale_matter_context_when_filter_changes(self):
        page = HTML[HTML.index("async function documentsPage(){"):HTML.index("\nasync function law(){")]
        self.assertIn("if(!matterSelect.value){currentDocuments=[];documentRows.replaceChildren();stats.replaceChildren();workspace.replaceChildren();uploadButton.disabled=true;uploadSubmit.disabled=true;summary.textContent=", page)

    def test_document_library_filters_are_driven_by_returned_document_metadata(self):
        page = HTML[HTML.index("async function documentsPage(){"):HTML.index("\nasync function law(){")]
        self.assertIn("const renderDocuments=docs=>{", page)
        self.assertIn("new Set(docs.map(doc=>String(doc.extraction_status", page)
        self.assertIn("doc.content_type", page)
        self.assertIn("documentFilter.oninput=()=>renderDocuments(currentDocuments)", page)
        self.assertIn("documentStatusFilter.onchange=()=>renderDocuments(currentDocuments)", page)

    def test_firm_switch_clears_selected_document_matter_context(self):
        self.assertIn("window.DOCUMENT_MATTER_ID=null;sessionStorage.me=JSON.stringify(ME)", HTML)

    def test_document_library_metrics_are_derived_from_selected_matter_records(self):
        page = HTML[HTML.index("async function documentsPage(){"):HTML.index("\nasync function law(){")]
        self.assertIn("docs.filter(doc=>['text_extracted','complete'].includes(doc.extraction_status)).length", page)
        self.assertIn("docs.filter(doc=>Boolean(doc.ocr_used)).length", page)
        self.assertIn("docs.filter(doc=>doc.ocr_used||!['text_extracted','complete'].includes(doc.extraction_status)||!doc.saved_classification).length", page)
        self.assertIn("Selected matter only", page)
        self.assertIn("Not a document-failure determination", page)

    def test_documents_page_uploads_pdf_and_docx_to_selected_matter(self):
        page = HTML[HTML.index("async function documentsPage(){"):HTML.index("\nasync function law(){")]
        self.assertIn("multiple:true", page)
        self.assertIn("accept:'.pdf,.docx,application/pdf", page)
        self.assertIn("item.file.size<=15000000", page)
        self.assertIn("'/cases/'+encodeURIComponent(matterId)+'/upload'", page)
        self.assertIn("credentials:'same-origin'", page)
        self.assertIn("'X-CSRF-Token':decodeURIComponent(csrf)", page)
        self.assertIn("if(succeeded)await loadMatter()", page)
        self.assertIn("role:'button',tabIndex:0", page)
        self.assertIn("is-dragover", page)

    def test_document_library_matter_picker_uses_bounded_server_pagination(self):
        page = HTML[HTML.index("async function documentsPage(){"):HTML.index("\nasync function law(){")]
        self.assertIn("const matterLimit=50", page)
        self.assertIn("limit:String(matterLimit)", page)
        self.assertIn("offset:String(matterOffset)", page)
        self.assertIn("matterTotal", page)
        self.assertIn("nextMatter.disabled=matterOffset+matterLimit>=matterTotal", page)

    def test_document_upload_handles_expired_sessions_and_read_only_firms(self):
        page = HTML[HTML.index("async function documentsPage(){"):HTML.index("\nasync function law(){")]
        self.assertIn("response.status===401", page)
        self.assertIn("response.status===423", page)
        self.assertIn("This firm is read-only; contact your firm administrator.", page)

    def test_document_library_filters_saved_classification_state(self):
        page = HTML[HTML.index("async function documentsPage(){"):HTML.index("\nasync function law(){")]
        self.assertIn("documentClassificationFilter", page)
        self.assertIn("documentClassificationFilter.value==='saved'?!!doc.saved_classification:!doc.saved_classification", page)
        self.assertIn("documentClassificationFilter.onchange=()=>renderDocuments(currentDocuments)", page)

    def test_workspace_global_search_uses_authorized_bounded_matter_search(self):
        shell = HTML[HTML.index("function shell(title"):HTML.index("\nfunction mfaFirmSwitcher()")]
        self.assertIn("Global search across accessible matters", shell)
        self.assertIn("limit:'8',offset:'0'", shell)
        self.assertIn("api('/cases/search?'+params.toString())", shell)
        self.assertIn("globalSearchInput.onkeydown", shell)
        self.assertIn("globalSearchInput.oninput=()=>globalSearchResults.replaceChildren()", shell)
        self.assertIn("view(item.id)", shell)

    def test_document_context_resets_upload_queue_and_filters_between_matters(self):
        page = HTML[HTML.index("async function documentsPage(){"):HTML.index("\nasync function law(){")]
        self.assertIn("uploadResults.replaceChildren();uploadStatus.textContent='';uploadInput.value=''", page)
        self.assertIn("documentFilter.value='';documentTypeFilter.value='';documentStatusFilter.value='';documentClassificationFilter.value=''", page)

    def test_sidebar_uses_lexora_brand_identity_from_figma(self):
        self.assertIn("className:'brand-name',textContent:'Lexora'", HTML)
        self.assertIn("className:'brand-subtitle'", HTML)
        self.assertIn("#side .brand-name", HTML)

    def test_document_library_supports_pdf_docx_file_type_filter(self):
        page = HTML[HTML.index("async function documentsPage(){"):HTML.index("\nasync function law(){")]
        self.assertIn("documentTypeFilter", page)
        self.assertIn("documentTypeFilter.value==='pdf'", page)
        self.assertIn("wordprocessingml", page)
        self.assertIn("documentTypeFilter.onchange=()=>renderDocuments(currentDocuments)", page)

    def test_document_analysis_loads_classification_alongside_extracted_chunks(self):
        self.assertIn("const [data,classification]=await Promise.all([api('/cases/'+caseId+'/docs/'+doc.document_id+'/chunks'),api('/cases/'+caseId+'/docs/'+doc.document_id+'/classification').catch(()=>null)])", HTML)

    def test_document_library_localizes_extraction_statuses(self):
        page = HTML[HTML.index("async function documentsPage(){"):HTML.index("\nasync function law(){")]
        self.assertIn("const statusNames=", page)
        self.assertIn("ocr_unverified", page)
        self.assertIn("partial_text_ocr_unavailable", page)
        self.assertIn("new Option(statusName(value),value)", page)

    def test_document_matter_picker_shows_case_and_client_context(self):
        page = HTML[HTML.index("async function documentsPage(){"):HTML.index("\nasync function law(){")]
        self.assertIn("m.case_number", page)
        self.assertIn("m.case_year", page)
        self.assertIn("m.client", page)
        self.assertIn("m.opposing_party", page)

    def test_original_download_handles_expired_session_and_purged_object(self):
        page = HTML[HTML.index("async function documentsPage(){"):HTML.index("\nasync function law(){")]
        self.assertIn("const downloadOriginal=async doc=>", page)
        self.assertIn("response.status===404", page)
        self.assertIn("Original file is unavailable or was purged under the retention policy.", page)
        self.assertIn("URL.createObjectURL(blob)", page)

    def test_document_library_filters_saved_categories_and_normalizes_arabic_search(self):
        page = HTML[HTML.index("async function documentsPage(){"):HTML.index("\\nasync function law(){")]
        self.assertIn("clearDocumentFilters=btn", page)
        self.assertIn("normalizeLibrarySearch", page)
        self.assertIn("replace(/[أإآٱ]/g,'ا')", page)
        self.assertIn("replace(/[٠-٩]/g", page)
        self.assertIn("Object.entries(categoryNames)", page)
        self.assertIn("doc.saved_classification===classificationValue", page)

    def test_language_switch_preserves_documents_workspace(self):
        self.assertIn("if(PAGE==='documents')documentsPage();else if(window.CASE_ID)", HTML)

    def test_document_filter_row_has_room_for_reset_action_and_stacks_on_mobile(self):
        self.assertIn("repeat(3,minmax(130px,180px)) auto", HTML)
        self.assertIn("@media(max-width:700px){#main .document-library-filter>.row{grid-template-columns:minmax(0,1fr)}}", HTML)

    def test_accessible_documents_global_view_uses_permission_filtered_api_and_paging(self):
        page = HTML[HTML.index("async function documentsPage(){"):HTML.index("\\nasync function law(){")]
        self.assertIn("All documents I can access", page)
        self.assertIn("api('/documents/search?'+params.toString())", page)
        self.assertIn("globalOffset", page)
        self.assertIn("doc.case_id", page)
        self.assertIn("Open matter", page)
        self.assertIn("Metadata results only", page)

    def test_global_document_open_matter_adds_paged_case_to_selector(self):
        page = HTML[HTML.index("async function documentsPage(){"):HTML.index("\\nasync function law(){")]
        self.assertIn("Array.from(matterSelect.options).some(option=>option.value===value)", page)
        self.assertIn("matterSelect.add(new Option", page)
        self.assertIn("list.hidden=true", page)

    def test_cross_matter_text_search_ui_is_bilingual_and_warns_about_unverified_excerpts(self):
        page = HTML[HTML.index("async function documentsPage(){"):HTML.index("\\nasync function law(){")]
        self.assertIn("api('/documents/search-text?'", page)
        self.assertIn("Search extracted text across accessible matters", page)
        self.assertIn("results are extracted-text matches, not verified facts or legal conclusions", page)
        self.assertIn("item.page", page)
        self.assertIn("item.excerpt", page)

    def test_cross_matter_text_search_results_are_paginated(self):
        page = HTML[HTML.index("async function documentsPage(){"):HTML.index("\\nasync function law(){")]
        self.assertIn("textSearchOffset", page)
        self.assertIn("textSearchTotal", page)
        self.assertIn("offset:String(textSearchOffset)", page)
        self.assertIn("previousTextSearch", page)
        self.assertIn("nextTextSearch", page)

    def test_document_file_icons_do_not_mislabel_non_docx_files_as_word(self):
        page = HTML[HTML.index("async function documentsPage(){"):HTML.index("\\nasync function law(){")]
        self.assertIn("endsWith('.docx')?'DOCX':'FILE'", page)

    def test_figma_theme_keeps_destructive_actions_red_and_disabled_states_visible(self):
        self.assertIn("#main button.d{background:var(--bad)", HTML)
        self.assertIn("#main button:disabled{opacity:.55;cursor:not-allowed}", HTML)

    def test_documents_workspace_defaults_to_authorized_library_when_no_matter_is_selected(self):
        page = HTML[HTML.index("async function documentsPage(){"):HTML.index("\\nasync function law(){")]
        self.assertIn("await loadMatters();", page)
        self.assertIn("if(!matterSelect.value)await loadAllAccessibleDocs();", page)
        self.assertIn("list.hidden=!list.children.length", page)

    def test_global_document_metric_uses_compact_single_column_layout(self):
        self.assertIn(".document-library-stats.global-document-stats{grid-template-columns:minmax(0,1fr)}", HTML)
        self.assertIn("stats.classList.add('global-document-stats')", HTML)
        self.assertIn("stats.classList.remove('global-document-stats')", HTML)

    def test_legal_research_source_caution_has_explicit_verification_heading(self):
        self.assertIn("Recorded source status: verified operative text", HTML)
        self.assertIn("Source verification warning", HTML)
        self.assertIn("#main .research-source-caution strong{display:block", HTML)

    def test_legal_research_summarizes_source_verification_before_citations(self):
        self.assertIn("const cautionCount=sourceItems.filter", HTML)
        self.assertIn("Source verification required", HTML)
        self.assertIn("of '+sourceItems.length+' sources need verification", HTML)
        self.assertIn("Recorded verification status", HTML)

    def test_multi_file_upload_reports_per_file_progress(self):
        self.assertIn("for(const [index,item] of valid.entries())", HTML)
        self.assertIn("index+1)+' / '+valid.length", HTML)
        self.assertIn("uploadPanel.setAttribute('aria-busy','true')", HTML)
        self.assertIn("uploadPanel.setAttribute('aria-busy','false')", HTML)

if __name__ == "__main__":
    unittest.main()
