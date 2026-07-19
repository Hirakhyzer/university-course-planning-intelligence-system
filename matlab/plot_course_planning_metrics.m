function plot_course_planning_metrics(outputDir)
%PLOT_COURSE_PLANNING_METRICS Plot synthetic course-planning metrics.
% Usage: plot_course_planning_metrics('outputs')

if nargin < 1
    outputDir = 'outputs';
end

riskPath = fullfile(outputDir, 'results', 'synthetic_graduation_risk.csv');
planPath = fullfile(outputDir, 'results', 'synthetic_student_plan_summary.csv');
figDir = fullfile(outputDir, 'figures');
if ~exist(figDir, 'dir')
    mkdir(figDir);
end

risk = readtable(riskPath);
plan = readtable(planPath);

figure;
histogram(risk.graduation_risk_score);
title('Synthetic graduation risk score distribution');
xlabel('Risk score'); ylabel('Students');
saveas(gcf, fullfile(figDir, 'matlab_graduation_risk_histogram.png'));

figure;
histogram(plan.recommended_credits);
title('Synthetic recommended credit distribution');
xlabel('Recommended credits'); ylabel('Students');
saveas(gcf, fullfile(figDir, 'matlab_recommended_credits_histogram.png'));
end
