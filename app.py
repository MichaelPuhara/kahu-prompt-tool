import streamlit as st
import pandas as pd
import uuid
from datetime import datetime
from pathlib import Path

# Simple config
CONFIG = {
    'data_dir': Path('data'),
    'element_types': ['role', 'goal', 'audience', 'context', 'output', 'tone'],
}
CONFIG['data_dir'].mkdir(exist_ok=True)

# Simple theme
st.markdown("""
<style>
.stApp { background: #0F0F0F; color: #FAFAFA; }
.main-header { 
    text-align: center; font-size: 2.5rem; font-weight: 700;
    background: linear-gradient(135deg, #0066CC, #3B82F6);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 2rem;
}
.kahu-brand { 
    color: #0066CC; font-size: 1.5rem; font-weight: 600; 
    text-align: center; margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

# Simple data functions
def load_data(filename):
    filepath = CONFIG['data_dir'] / filename
    if filepath.exists():
        return pd.read_csv(filepath)
    return pd.DataFrame()

def save_data(df, filename):
    filepath = CONFIG['data_dir'] / filename
    df.to_csv(filepath, index=False)

def main():
    st.set_page_config(page_title="kahu.code - Prompt Tool", page_icon="🎯", layout="wide")
    
    # Header
    st.markdown('<div class="kahu-brand">kahu.code</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="main-header">🎯 Enhanced Prompt Tool</h1>', unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["🎯 Create Elements", "🏗️ Build Prompts", "📚 Browse Prompts"])
    
    with tab1:
        st.markdown("### Create New Element")
        col1, col2 = st.columns(2)
        
        with col1:
            element_type = st.selectbox("Type", CONFIG['element_types'])
            title = st.text_input("Title")
        
        with col2:
            content = st.text_area("Content", height=150)
        
        if st.button("💾 Save Element", type="primary"):
            if title and content:
                # Load existing data
                df = load_data('elements.csv')
                if df.empty:
                    df = pd.DataFrame(columns=['id', 'title', 'type', 'content', 'created_at'])
                
                # Add new element
                new_row = pd.DataFrame({
                    'id': [str(uuid.uuid4())],
                    'title': [title],
                    'type': [element_type],
                    'content': [content],
                    'created_at': [datetime.now()]
                })
                df = pd.concat([df, new_row], ignore_index=True)
                save_data(df, 'elements.csv')
                st.success("✅ Element saved!")
                st.rerun()
    
    with tab2:
        st.markdown("### Build Your Prompt")
        df = load_data('elements.csv')
        
        if df.empty:
            st.warning("Create some elements first!")
        else:
            prompt_parts = []
            
            for section in ['role', 'goal', 'audience', 'context', 'output', 'tone']:
                section_elements = df[df['type'] == section]
                if not section_elements.empty:
                    st.markdown(f"**{section.title()}**")
                    selected = st.selectbox(f"Choose {section}",
                                          ["Skip"] + section_elements['title'].tolist(),
                                          key=section)
                    
                    if selected != "Skip":
                        content = section_elements[section_elements['title'] == selected]['content'].iloc[0]
                        prompt_parts.append(f"{section.title()}: {content}")
            
            if prompt_parts:
                prompt = "\n\n".join(prompt_parts)
                st.markdown("### Generated Prompt")
                st.text_area("Your prompt:", value=prompt, height=200)
                
                # Save prompt
                prompt_name = st.text_input("Save as:")
                if st.button("💾 Save Prompt") and prompt_name:
                    prompts_df = load_data('prompts.csv')
                    if prompts_df.empty:
                        prompts_df = pd.DataFrame(columns=['id', 'name', 'prompt', 'created_at'])
                    
                    new_prompt = pd.DataFrame({
                        'id': [str(uuid.uuid4())],
                        'name': [prompt_name],
                        'prompt': [prompt],
                        'created_at': [datetime.now()]
                    })
                    prompts_df = pd.concat([prompts_df, new_prompt], ignore_index=True)
                    save_data(prompts_df, 'prompts.csv')
                    st.success("✅ Prompt saved!")
    
    with tab3:
        st.markdown("### Saved Prompts")
        prompts_df = load_data('prompts.csv')
        
        if prompts_df.empty:
            st.info("No saved prompts yet.")
        else:
            for _, row in prompts_df.iterrows():
                with st.expander(f"📝 {row['name']}"):
                    st.text_area("Prompt", value=row['prompt'], height=150, key=f"view_{row['id']}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        Made with ❤️ by <a href="https://kahuco.de" style="color: #0066CC;">kahu.code</a>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
