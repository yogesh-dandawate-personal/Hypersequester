/**
 * Custom hook for managing assessments
 */

import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { assessmentsAPI, processingAPI, handleApiError } from '../utils/api';
import { message } from 'antd';

export const useAssessments = (filters = {}) => {
  const queryClient = useQueryClient();

  // Fetch assessments
  const {
    data: assessments,
    isLoading,
    error,
    refetch,
  } = useQuery(
    ['assessments', filters],
    () => assessmentsAPI.getAll(filters),
    {
      select: (response) => response.data,
      onError: (error) => {
        const errorInfo = handleApiError(error);
        message.error(`Failed to load assessments: ${errorInfo.message}`);
      },
    }
  );

  // Create assessment mutation
  const createAssessmentMutation = useMutation(
    (assessmentData) => assessmentsAPI.create(assessmentData),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['assessments']);
        message.success('Assessment created successfully');
      },
      onError: (error) => {
        const errorInfo = handleApiError(error);
        message.error(`Failed to create assessment: ${errorInfo.message}`);
      },
    }
  );

  // Update assessment mutation
  const updateAssessmentMutation = useMutation(
    ({ id, data }) => assessmentsAPI.update(id, data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['assessments']);
        message.success('Assessment updated successfully');
      },
      onError: (error) => {
        const errorInfo = handleApiError(error);
        message.error(`Failed to update assessment: ${errorInfo.message}`);
      },
    }
  );

  // Delete assessment mutation
  const deleteAssessmentMutation = useMutation(
    (id) => assessmentsAPI.delete(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['assessments']);
        message.success('Assessment deleted successfully');
      },
      onError: (error) => {
        const errorInfo = handleApiError(error);
        message.error(`Failed to delete assessment: ${errorInfo.message}`);
      },
    }
  );

  return {
    assessments: assessments || [],
    isLoading,
    error,
    refetch,
    createAssessment: createAssessmentMutation.mutate,
    updateAssessment: updateAssessmentMutation.mutate,
    deleteAssessment: deleteAssessmentMutation.mutate,
    isCreating: createAssessmentMutation.isLoading,
    isUpdating: updateAssessmentMutation.isLoading,
    isDeleting: deleteAssessmentMutation.isLoading,
  };
};

export const useAssessment = (assessmentId) => {
  // Fetch single assessment
  const {
    data: assessment,
    isLoading,
    error,
    refetch,
  } = useQuery(
    ['assessment', assessmentId],
    () => assessmentsAPI.getById(assessmentId),
    {
      enabled: !!assessmentId,
      select: (response) => response.data,
      onError: (error) => {
        const errorInfo = handleApiError(error);
        message.error(`Failed to load assessment: ${errorInfo.message}`);
      },
    }
  );

  // Fetch assessment results
  const {
    data: results,
    isLoading: isLoadingResults,
    error: resultsError,
    refetch: refetchResults,
  } = useQuery(
    ['assessment-results', assessmentId],
    () => assessmentsAPI.getResults(assessmentId),
    {
      enabled: !!assessmentId && assessment?.status === 'completed',
      select: (response) => response.data,
      onError: (error) => {
        const errorInfo = handleApiError(error);
        message.error(`Failed to load results: ${errorInfo.message}`);
      },
    }
  );

  return {
    assessment,
    results,
    isLoading,
    isLoadingResults,
    error: error || resultsError,
    refetch,
    refetchResults,
  };
};

export const useProcessingStatus = (jobId, enabled = true) => {
  const [status, setStatus] = useState(null);
  const [progress, setProgress] = useState(0);

  const {
    data: statusData,
    isLoading,
    error,
  } = useQuery(
    ['processing-status', jobId],
    () => processingAPI.getStatus(jobId),
    {
      enabled: enabled && !!jobId,
      refetchInterval: (data) => {
        // Stop polling if job is completed or failed
        const status = data?.data?.status;
        return status === 'pending' || status === 'processing' ? 2000 : false;
      },
      select: (response) => response.data,
      onSuccess: (data) => {
        setStatus(data.status);
        setProgress(data.progress || 0);
      },
      onError: (error) => {
        const errorInfo = handleApiError(error);
        console.error(`Failed to get processing status: ${errorInfo.message}`);
      },
    }
  );

  return {
    status,
    progress,
    isLoading,
    error,
    data: statusData,
  };
};

export const useAssessmentActions = () => {
  const queryClient = useQueryClient();

  // Download report
  const downloadReport = async (assessmentId, filename) => {
    try {
      const response = await assessmentsAPI.downloadReport(assessmentId);
      const blob = new Blob([response.data], { type: 'application/json' });
      
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename || `assessment_${assessmentId}_report.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      message.success('Report downloaded successfully');
    } catch (error) {
      const errorInfo = handleApiError(error);
      message.error(`Failed to download report: ${errorInfo.message}`);
    }
  };

  // Download KML
  const downloadKML = async (assessmentId, filename) => {
    try {
      const response = await assessmentsAPI.downloadKML(assessmentId);
      const blob = new Blob([response.data], { type: 'application/vnd.google-earth.kml+xml' });
      
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename || `assessment_${assessmentId}.kml`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      message.success('KML file downloaded successfully');
    } catch (error) {
      const errorInfo = handleApiError(error);
      message.error(`Failed to download KML: ${errorInfo.message}`);
    }
  };

  // Cancel processing job
  const cancelJob = useMutation(
    (jobId) => processingAPI.cancelJob(jobId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['assessments']);
        queryClient.invalidateQueries(['processing-status']);
        message.success('Processing job cancelled');
      },
      onError: (error) => {
        const errorInfo = handleApiError(error);
        message.error(`Failed to cancel job: ${errorInfo.message}`);
      },
    }
  );

  return {
    downloadReport,
    downloadKML,
    cancelJob: cancelJob.mutate,
    isCancelling: cancelJob.isLoading,
  };
};
