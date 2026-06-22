import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import io
from datetime import datetime

# Import local engines
from data_generator import generate_sample_data
from reconciliation_engine import reconcile_statements, generate_reconciliation_summary, export_reconciliation_excel

# Streamlit App Configurations
st.set_page_config(
    page_title="نظام أتمتة التسويات البنكية",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium CSS Styling (Vibrant Neon violet/blue accents matching portfolio theme)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap');
    
    /* Force Cairo font globally */
    html, body, [class*="css"], [class*="st-"] {
        font-family: 'Cairo', sans-serif !important;
        text-align: right;
        direction: RTL;
    }
    
    /* Force main app background to premium deep violet dark gradient */
    .stApp {
        background: radial-gradient(circle at top right, #1b133a, #0b0816, #05040a) !important;
        background-attachment: fixed !important;
    }
    
    /* Title and description styles */
    .main-title {
        background: linear-gradient(135deg, #d8b4fe, #a78bfa, #8b5cf6) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        font-size: 38px !important;
        font-weight: 800 !important;
        margin-bottom: 8px !important;
        text-shadow: 0 0 30px rgba(139, 92, 246, 0.15);
        text-align: right;
    }
    
    .sub-title {
        color: #b3b9c9 !important;
        font-size: 16px !important;
        margin-bottom: 25px !important;
        text-align: right;
    }
    
    /* Premium glassmorphic cards */
    .card {
        background: rgba(22, 17, 47, 0.65) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(139, 92, 246, 0.3) !important;
        padding: 24px;
        border-radius: 16px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
    }
    
    .card h1, .card h2, .card h3, .card h4, .card h5, .card h6, .card p, .card li, .card ul, .card b, .card span {
        color: #ffffff !important;
    }
    
    .metric-value {
        font-size: 26px;
        font-weight: 700;
        color: #ffffff !important;
        text-shadow: 0 0 10px rgba(139, 92, 246, 0.5);
    }
    
    .metric-label {
        font-size: 14px;
        color: #d8b4fe !important;
        font-weight: 600;
    }
    
    /* Custom Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0b0816 !important;
        border-left: 1px solid rgba(139, 92, 246, 0.25) !important;
        box-shadow: 5px 0 25px rgba(0, 0, 0, 0.5);
    }
    
    /* Force sidebar text to be bright and clear */
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3, 
    section[data-testid="stSidebar"] h4, 
    section[data-testid="stSidebar"] h5, 
    section[data-testid="stSidebar"] h6,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] div,
    section[data-testid="stSidebar"] label {
        color: #ffffff !important;
    }
    
    /* Custom file uploader buttons and borders */
    div[data-testid="stFileUploader"] {
        background-color: rgba(22, 17, 47, 0.5) !important;
        border: 1px dashed rgba(139, 92, 246, 0.5) !important;
        border-radius: 12px !important;
        padding: 12px !important;
        transition: border 0.3s ease;
    }
    div[data-testid="stFileUploader"]:hover {
        border-color: #a78bfa !important;
        box-shadow: 0 0 10px rgba(139, 92, 246, 0.2);
    }
    div[data-testid="stFileUploader"] section {
        background-color: transparent !important;
    }
    
    /* Premium button animations and style */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #7c3aed, #a78bfa) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-family: 'Cairo', sans-serif !important;
        font-size: 16px !important;
        padding: 12px 24px !important;
        transition: 0.3s all ease !important;
        box-shadow: 0 4px 15px rgba(124, 58, 237, 0.35);
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #8b5cf6, #c084fc) !important;
        box-shadow: 0 0 25px rgba(139, 92, 246, 0.7) !important;
        transform: translateY(-2px);
    }
    .stButton>button:active {
        transform: translateY(1px);
    }
    
    /* Download button specific styles */
    div[data-testid="stDownloadButton"] button {
        background: linear-gradient(135deg, #10b981, #34d399) !important;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.35) !important;
    }
    div[data-testid="stDownloadButton"] button:hover {
        background: linear-gradient(135deg, #059669, #10b981) !important;
        box-shadow: 0 0 25px rgba(16, 185, 129, 0.7) !important;
    }
    
    /* Tabs styling */
    button[data-baseweb="tab"] {
        font-family: 'Cairo', sans-serif !important;
        color: #9ca3af !important;
        font-size: 16px !important;
        border-bottom-width: 2px !important;
        transition: all 0.3s ease;
    }
    button[data-baseweb="tab"]:hover {
        color: #e9d5ff !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #c084fc !important;
        border-bottom-color: #a78bfa !important;
        font-weight: bold !important;
    }
    
    .success-box {
        background-color: rgba(16, 185, 129, 0.15) !important;
        border: 1px solid rgba(16, 185, 129, 0.4) !important;
        color: #34d399 !important;
        padding: 16px;
        border-radius: 12px;
        font-weight: 700;
        margin-bottom: 24px;
        text-align: right;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.1);
    }
    
    .alert-box {
        background-color: rgba(239, 68, 68, 0.15) !important;
        border: 1px solid rgba(239, 68, 68, 0.4) !important;
        color: #f87171 !important;
        padding: 16px;
        border-radius: 12px;
        font-weight: 700;
        margin-bottom: 24px;
        text-align: right;
        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.1);
    }
    
    /* Custom style for plotly charts background */
    div[data-testid="stPlotlyChart"] {
        background-color: rgba(22, 17, 47, 0.4) !important;
        border: 1px solid rgba(139, 92, 246, 0.2) !important;
        border-radius: 16px !important;
        padding: 10px !important;
    }
    
    /* Tables and dataframes wrapper */
    div[data-testid="stDataFrame"] {
        background-color: rgba(22, 17, 47, 0.45) !important;
        border: 1px solid rgba(139, 92, 246, 0.25) !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }
    
    /* Adjust text colors in sub-headers */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Cairo', sans-serif !important;
        text-align: right;
        color: #ffffff !important;
    }
    
    /* Info box styling */
    div[data-testid="stNotification"] {
        background-color: rgba(30, 41, 59, 0.7) !important;
        border: 1px solid rgba(148, 163, 184, 0.3) !important;
        border-radius: 12px !important;
    }
    div[data-testid="stNotification"] div {
        color: #f1f5f9 !important;
    }
    
    </style>
""", unsafe_allow_html=True)

# ----------------- Helper Functions -----------------
def load_excel_file(uploaded_file):
    try:
        return pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"حدث خطأ أثناء قراءة الملف: {e}")
        return None

# ----------------- Main UI -----------------
st.markdown("<h1 class='main-title'>🏦 نظام أتمتة التسويات البنكية اليومية</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>أداة محاسبية ذكية لربط ومطابقة معاملات كشف الحساب البنكي مع الأستاذ العام وتحديد الفروقات تلقائياً بدقة 100%.</p>", unsafe_allow_html=True)

# ----------------- Sidebar -----------------
st.sidebar.markdown("### ⚙️ لوحة التحكم والإعدادات")

# 1. Sample Data Section
st.sidebar.markdown("---")
st.sidebar.markdown("#### 📊 عينات البيانات التجريبية")
st.sidebar.info("إذا لم تكن تمتلك ملفات جاهزة، يمكنك إنشاء وتنزيل ملفات كشف حساب البنك ودفتر الأستاذ التجريبي لتجربة عملية المطابقة فوراً.")

temp_dir = os.path.dirname(os.path.abspath(__file__))
if st.sidebar.button("⚙️ توليد ملفات العينات المحاسبية"):
    bank_path, ledger_path = generate_sample_data(temp_dir)
    st.sidebar.success("تم توليد الملفات بنجاح!")
    
    # Read files for download
    with open(bank_path, "rb") as f:
        st.sidebar.download_button(
            label="⬇️ تحميل كشف البنك التجريبي (Excel)",
            data=f,
            file_name="bank_statement_sample.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    with open(ledger_path, "rb") as f:
        st.sidebar.download_button(
            label="⬇️ تحميل دفتر الأستاذ التجريبي (Excel)",
            data=f,
            file_name="general_ledger_sample.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# 2. File Uploads
st.sidebar.markdown("---")
st.sidebar.markdown("#### 📁 رفع المستندات المالية")

uploaded_bank = st.sidebar.file_uploader("تحميل كشف حساب البنك (Excel)", type=["xlsx", "xls"])
uploaded_ledger = st.sidebar.file_uploader("تحميل دفتر الأستاذ العام (Excel)", type=["xlsx", "xls"])

# ----------------- Main Section -----------------
if not uploaded_bank or not uploaded_ledger:
    # App Welcome Page/Information when files are not loaded
    st.markdown("""
        <div class='card'>
            <h3 style='color: #8b5cf6;'>👋 مرحباً بك في نظام التسويات البنكية الذكي!</h3>
            <p>تعتبر تسوية الحسابات البنكية ومطابقتها مع دفاتر المحاسبة من العمليات الروتينية الشاقة التي تستهلك الوقت. يهدف هذا النظام إلى تبسيطها وأتمتتها في خطوات معدودة:</p>
            <ul>
                <li><b>مطابقة المعاملات تلقائياً:</b> يطابق النظام التروس المالية المزدوجة بالاعتماد على قيم المبالغ، والتواريخ، والمراجع البنكية.</li>
                <li><b>عزل الاختلافات المعلقة:</b> يقوم النظام بفصل الشيكات المعلقة، الإيداعات بالطريق، الفوائد البنكية، والعمولات غير المسجلة.</li>
                <li><b>مذكرة تسوية مطابقة:</b> توليد مذكرة التسوية الرسمية (Bank Reconciliation) والتأكد من تطابق أرصدة الطرفين.</li>
                <li><b>تصدير التقارير:</b> تصدير نتائج التسوية كملف إكسل متكامل وجاهز للطباعة والمراجعة.</li>
            </ul>
            <p style='color: #a78bfa; font-weight: bold;'>👈 للبدء، يرجى رفع ملف كشف البنك ودفتر الأستاذ العام من الشريط الجانبي (يمكنك استخدام زر توليد العينات لتجربة النظام).</p>
        </div>
    """, unsafe_allow_html=True)
else:
    # Read files
    df_bank_raw = load_excel_file(uploaded_bank)
    df_ledger_raw = load_excel_file(uploaded_ledger)
    
    if df_bank_raw is not None and df_ledger_raw is not None:
        # Check columns preview
        st.markdown("### 📊 معاينة وفحص البيانات المرفوعة")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("##### 🏦 كشف حساب البنك (أول 3 حركات)")
            st.dataframe(df_bank_raw.head(3), use_container_width=True)
        with col2:
            st.markdown("##### 📖 دفتر الأستاذ العام (أول 3 حركات)")
            st.dataframe(df_ledger_raw.head(3), use_container_width=True)
            
        # Verify required columns for automation
        bank_cols = ['التاريخ', 'البيان', 'المرجع', 'المدين (مسحوبات)', 'الدائن (إيداعات)', 'الرصيد']
        ledger_cols = ['التاريخ', 'رقم القيد/المستند', 'الشرح', 'المدين', 'الدائن', 'الرصيد']
        
        bank_valid = all(col in df_bank_raw.columns for col in bank_cols)
        ledger_valid = all(col in df_ledger_raw.columns for col in ledger_cols)
        
        if not bank_valid or not ledger_valid:
            st.error("⚠️ ملفات الإكسل المرفوعة لا تتطابق مع الهيكل المطلوب. يرجى التأكد من احتواء الملفات على الأعمدة القياسية مثل (التاريخ، البيان/الشرح، المرجع، الرصيد، المدين، والدائن) أو استخدام مولد العينات التجريبية للحصول على التنسيق الصحيح.")
        else:
            # Let's run reconciliation
            if st.button("🚀 تشغيل عملية التسوية والمطابقة الآلية"):
                with st.spinner("جاري معالجة البيانات ومطابقة القيود..."):
                    df_matched_b, df_unmatched_b, df_matched_l, df_unmatched_l = reconcile_statements(df_bank_raw, df_ledger_raw)
                    summary = generate_reconciliation_summary(df_bank_raw, df_ledger_raw, df_unmatched_b, df_unmatched_l)
                    
                    st.success("تمت عملية المطابقة بنجاح!")
                    
                    # 1. Reconciled Status Box
                    if abs(summary['unreconciled_difference']) < 0.01:
                        st.markdown("<div class='success-box'>✅ تم تسوية الحسابات البنكية بنجاح! الرصيد المعدل للطرفين متطابق تماماً، والفرق غير المسوى يساوي 0.00 جنيه مصري.</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='alert-box'>⚠️ تنبيه: الحسابات غير مطابقة بالكامل. هناك فروق غير مسواة بقيمة {summary['unreconciled_difference']:,.2f} جنيه مصري بحاجة للمراجعة.</div>", unsafe_allow_html=True)
                        
                    # 2. Reconciled KPIs Grid
                    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
                    with kpi1:
                        st.markdown(f"""
                            <div class='card'>
                                <div class='metric-value'>{summary['bank_ending_balance']:,.2f}</div>
                                <div class='metric-label'>رصيد كشف البنك الفعلي</div>
                            </div>
                        """, unsafe_allow_html=True)
                    with kpi2:
                        st.markdown(f"""
                            <div class='card'>
                                <div class='metric-value'>{summary['ledger_ending_balance']:,.2f}</div>
                                <div class='metric-label'>رصيد الدفاتر الدفتري</div>
                            </div>
                        """, unsafe_allow_html=True)
                    with kpi3:
                        st.markdown(f"""
                            <div class='card'>
                                <div class='metric-value'>{summary['adjusted_bank_balance']:,.2f}</div>
                                <div class='metric-label'>رصيد البنك المعدل</div>
                            </div>
                        """, unsafe_allow_html=True)
                    with kpi4:
                        st.markdown(f"""
                            <div class='card'>
                                <div class='metric-value'>{summary['adjusted_ledger_balance']:,.2f}</div>
                                <div class='metric-label'>رصيد الدفاتر المعدل</div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                    # 3. Chart Analysis Section
                    col_chart, col_btn = st.columns([2, 1])
                    with col_chart:
                        # Pie chart of matched vs unmatched count
                        total_bank_trans = len(df_bank_raw)
                        matched_count = len(df_matched_b)
                        unmatched_count = len(df_unmatched_b)
                        
                        fig = go.Figure(data=[go.Pie(
                            labels=['حركات مطابقة', 'حركات معلقة / فروقات'],
                            values=[matched_count, unmatched_count],
                            hole=.4,
                            marker_colors=['#10b981', '#ef4444']
                        )])
                        fig.update_layout(
                            title_text="نسبة الحركات المطابقة والمعلقة بكشف البنك",
                            title_x=0.5,
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            font=dict(color='#ffffff')
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                    with col_btn:
                        st.markdown("##### 📁 تصدير التقرير المالي المعتمد")
                        st.write("يمكنك تحميل ملف إكسل منسق محاسبياً يحتوي على مذكرة تسوية البنك وكافة جداول الحركات المطابقة والمعلقة بشكل مستقل للمراجعة والأرشفة.")
                        
                        excel_report = export_reconciliation_excel(
                            summary, df_matched_b, df_unmatched_b, df_matched_l, df_unmatched_l
                        )
                        
                        st.download_button(
                            label="⬇️ تحميل تقرير تسوية البنك المكتمل (Excel)",
                            data=excel_report,
                            file_name=f"bank_reconciliation_report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                        
                    # 4. Detailed tabs
                    st.markdown("### 📋 جداول المعاملات التفصيلية")
                    tab1, tab2, tab3, tab4 = st.tabs(["📝 مذكرة تسوية البنك", "🏦 معلقات البنك", "📖 معلقات الدفاتر", "✅ العمليات المطابقة"])
                    
                    with tab1:
                        st.markdown("##### مذكرة تسوية البنك الرسمية")
                        
                        summary_rows = [
                            {"البند": "رصيد الحساب الجاري حسب كشف حساب البنك", "القيمة (جنيه مصري)": f"{summary['bank_ending_balance']:,.2f}"},
                            {"البند": "(+) يضاف: الإيداعات بالطريق (إيداعات بالدفاتر لم تظهر بالبنك)", "القيمة (جنيه مصري)": f"{summary['total_deposits_in_transit']:,.2f}"},
                            {"البند": "(-) يخصم: شيكات صادرة معلقة (لم تقدم للصرف بالبنك)", "القيمة (جنيه مصري)": f"-{summary['total_outstanding_checks']:,.2f}"},
                            {"البند": "رصيد البنك المعدل المطبق", "القيمة (جنيه مصري)": f"{summary['adjusted_bank_balance']:,.2f}"},
                            {"البند": "رصيد النقدية بالبنك حسب دفاتر الأستاذ العام", "القيمة (جنيه مصري)": f"{summary['ledger_ending_balance']:,.2f}"},
                            {"البند": "(+) يضاف: مقبوضات وتحويلات واردة بالبنك لم تسجل بالدفاتر", "القيمة (جنيه مصري)": f"{summary['total_direct_credits']:,.2f}"},
                            {"البند": "(-) يخصم: العمولات والمصاريف البنكية غير المسجلة", "القيمة (جنيه مصري)": f"-{summary['total_bank_charges']:,.2f}"},
                            {"البند": "رصيد الدفاتر المعدل المطبق", "القيمة (جنيه مصري)": f"{summary['adjusted_ledger_balance']:,.2f}"},
                            {"البند": "----------------------------------------------------------------", "القيمة (جنيه مصري)": ""},
                            {"البند": "الفروقات غير المسواة", "القيمة (جنيه مصري)": f"{summary['unreconciled_difference']:,.2f}"}
                        ]
                        df_sum = pd.DataFrame(summary_rows)
                        
                        def style_rows(row):
                            val_a = str(row['البند'])
                            styles = ['text-align: right;'] * len(row)
                            if "(+)" in val_a:
                                styles = ['color: #10b981; font-weight: bold;'] * len(row)
                            elif "(-)" in val_a:
                                styles = ['color: #ef4444; font-weight: bold;'] * len(row)
                            elif "المعدل" in val_a or "رصيد" in val_a:
                                styles = ['font-weight: bold; background-color: rgba(139, 92, 246, 0.08);'] * len(row)
                            elif "الفروقات" in val_a:
                                diff_val = summary['unreconciled_difference']
                                if abs(diff_val) < 0.01:
                                    styles = ['color: #10b981; font-weight: bold; background-color: rgba(16, 185, 129, 0.08);'] * len(row)
                                else:
                                    styles = ['color: #ef4444; font-weight: bold; background-color: rgba(239, 68, 68, 0.08);'] * len(row)
                            return styles
                            
                        styled_df_sum = df_sum.style.apply(style_rows, axis=1)
                        st.dataframe(styled_df_sum, use_container_width=True, hide_index=True)


                        
                    with tab2:
                        st.markdown("##### معلقات كشف حساب البنك (سحب/إيداع لم يسجل بالدفاتر)")
                        if not df_unmatched_b.empty:
                            st.dataframe(df_unmatched_b[['التاريخ', 'البيان', 'المرجع', 'المدين (مسحوبات)', 'الدائن (إيداعات)', 'الرصيد']], use_container_width=True, hide_index=True)
                        else:
                            st.info("لا توجد أي معاملات معلقة بكشف البنك. كافة الحركات مسجلة بالدفاتر!")
                            
                    with tab3:
                        st.markdown("##### معلقات دفتر الأستاذ العام (شيكات صادرة معلقة أو إيداعات بالطريق)")
                        if not df_unmatched_l.empty:
                            st.dataframe(df_unmatched_l[['التاريخ', 'رقم القيد/المستند', 'الشرح', 'المدين', 'الدائن', 'الرصيد']], use_container_width=True, hide_index=True)
                        else:
                            st.info("لا توجد أي معلقات بالدفاتر. كافة العمليات تم صرفها وتسويتها بالبنك!")
                            
                    with tab4:
                        st.markdown("##### العمليات التي تمت مطابقتها وتسويتها بنجاح")
                        df_matched_print = df_matched_b[['التاريخ', 'البيان', 'المرجع', 'net_amount', 'match_id', 'notes']].copy()
                        df_matched_print.columns = ['التاريخ', 'البيان', 'المرجع', 'المبلغ الصافي', 'كود المطابقة', 'ملاحظات المطابقة']
                        st.dataframe(df_matched_print, use_container_width=True, hide_index=True)
