// Configuração do relatório Allure 3 (npm run report). Exporta um objeto
// simples, sem o defineConfig, que só serve para autocompletar no editor.
const { GITHUB_ACTIONS, GITHUB_SERVER_URL, GITHUB_REPOSITORY, GITHUB_RUN_ID } = process.env;

export default {
  name: "qa-api-python",
  output: "./reports/allure-report",
  // Cada geração acrescenta uma linha a este arquivo, que alimenta as
  // tendências e a detecção de testes instáveis. No CI, ele é baixado do
  // relatório publicado no GitHub Pages antes de gerar o novo.
  historyPath: "./reports/history.jsonl",
  plugins: {
    awesome: {
      options: {
        // Um único index.html, que abre direto no navegador, sem servidor.
        singleFile: true,
        reportLanguage: "pt",
        // Agrupa os cenários pela Funcionalidade do .feature.
        groupBy: ["feature"],
        // No CI, o relatório mostra o link da execução que o gerou.
        ...(GITHUB_ACTIONS && {
          ci: {
            type: "github",
            url: `${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}/actions/runs/${GITHUB_RUN_ID}`,
            name: "GitHub Actions",
          },
        }),
      },
    },
  },
};
