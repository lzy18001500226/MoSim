"use client";

import { Button } from "@/components/ui/button";
import { CenteredSpinner } from "@/components/ui/spinner";
import { ConfirmDialog } from "@/components/ui/confirm-dialog";
import { useTranslations } from "next-intl";
import {
  EditRepositoryModal,
  useRepositoryDetail,
  RepositoryHeader,
  RepositoryInfoCard,
  GitProviderCard,
  WebhookSettingsCard,
  RepositoryTabs,
  CapabilitiesTab,
} from "@/app/(dashboard)/[org]/repositories/[id]/components";

interface Props {
  repositoryId: number;
  onBack: () => void;
}

export function InfraRepositoryDetail({ repositoryId, onBack }: Props) {
  const t = useTranslations();
  const {
    repository,
    loading,
    activeTab,
    showEditModal,
    deleteDialog,
    setActiveTab,
    setShowEditModal,
    loadRepository,
    handleDelete,
  } = useRepositoryDetail(repositoryId);

  if (loading) return <CenteredSpinner />;

  if (!repository) {
    return (
      <div className="py-12 text-center">
        <p className="mb-4 text-muted-foreground">{t("repositories.detail.notFound")}</p>
        <Button variant="outline" onClick={onBack}>
          {t("repositories.detail.backToList")}
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <RepositoryHeader
        repository={repository}
        onEdit={() => setShowEditModal(true)}
        onDelete={handleDelete}
      />

      <RepositoryTabs activeTab={activeTab} onTabChange={setActiveTab} />

      {activeTab === "info" && (
        <div className="grid gap-6 md:grid-cols-2">
          <RepositoryInfoCard repository={repository} />
          <GitProviderCard repository={repository} />
          <div className="md:col-span-2">
            <WebhookSettingsCard repository={repository} onStatusChange={loadRepository} />
          </div>
        </div>
      )}

      {activeTab === "extensions" && <CapabilitiesTab repositoryId={repositoryId} />}

      {showEditModal && (
        <EditRepositoryModal
          repository={repository}
          onClose={() => setShowEditModal(false)}
          onUpdated={() => {
            setShowEditModal(false);
            loadRepository();
          }}
        />
      )}

      <ConfirmDialog {...deleteDialog.dialogProps} />
    </div>
  );
}
